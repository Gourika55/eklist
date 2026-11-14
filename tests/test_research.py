import unittest,tempfile,json
from pathlib import Path
from unittest.mock import patch
import research as r
class ResearchTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=r.DB;r.DB=Path(self.tmp.name)/'research.sqlite'
  self.j={'id':'test','query':'test','status':'running','plan':{'fields':['location','collaborates_with']},'entities':[],'claims':[],'evidence':[],'sources':[],'gaps':[],'metrics':{'rejected_extractions':0}}
 def tearDown(self):r.DB=self.old;self.tmp.cleanup()
 def test_quote_validation_and_graph(self):
  d=r.store_doc(self.j,'https://example.org','Source','Alpha Foundation collaborates with Beta University in Rajasthan.')
  r.accept_extraction(self.j,d,{'records':[{'name':'Alpha Foundation','type':'organisation','attributes':[{'field':'location','value':'Rajasthan','quote':d['text']},{'field':'location','value':'Delhi','quote':d['text']}],'relationships':[{'predicate':'collaborates_with','target_name':'Beta University','quote':d['text']}]}]})
  self.assertEqual(len(self.j['claims']),2);self.assertEqual(self.j['metrics']['rejected_extractions'],1);self.assertEqual(len(self.j['entities']),2)
  self.assertEqual(r.results(self.j)[0]['location'],'Rajasthan');self.assertIn('Beta University',r.export_csv(self.j))
 def test_invented_quote_rejected(self):
  d=r.store_doc(self.j,'https://example.org','Source','Alpha Foundation works in Rajasthan.')
  r.accept_extraction(self.j,d,{'records':[{'name':'Alpha Foundation','attributes':[{'field':'location','value':'Delhi','quote':'Alpha Foundation works in Delhi.'}]}]})
  self.assertEqual(self.j['claims'],[])
 def test_same_names_different_sources_not_merged(self):
  a=r.entity(self.j,'Alpha','org','source1');b=r.entity(self.j,'Alpha','org','source2');self.assertNotEqual(a['id'],b['id'])
 def test_exact_identifier_link(self):
  a=r.entity(self.j,'Alpha','college','source1','aishe:C-1');b=r.entity(self.j,'ALPHA','college','source2','aishe:C-1');self.assertEqual(a['id'],b['id'])
 def test_private_addresses_blocked(self):
  for u in ['http://127.0.0.1','http://169.254.169.254','file:///etc/passwd','http://user:pass@example.com','http://example.com:9999']:
   with self.assertRaises(ValueError):r.public_address(u)
 def test_dns_pinning_rejects_mixed_private(self):
  with patch('socket.getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',443))]):
   with self.assertRaises(ValueError):r.public_address('https://example.com')
 def test_csv_and_html_parsing(self):
  self.assertIn('[row 2]',r.parse_source(b'name,state\nAlpha,Rajasthan','text/csv','https://example.com/a.csv'))
  self.assertNotIn('secret()',r.parse_source(b'<html><script>secret()</script><p>Hello world</p></html>','text/html','https://example.com'))
 def test_persistence_and_restart(self):
  r.save(self.j);r.recover();self.assertEqual(r.get('test')['status'],'interrupted')
 def test_flexible_fields(self):
  p=r.checked_plan({'fields':['battery_capacity','manufacturer','launch_date','bad field'],'entity_types':['product'],'limit':1000},'products')
  self.assertEqual(p['limit'],50);self.assertIn('battery_capacity',p['fields']);self.assertNotIn('bad field',p['fields'])
 def test_csv_formula_safe(self):
  self.j['entities']=[{'id':'a','name':'=CMD()','type':'test'}]
  self.assertIn("'=CMD()",r.export_csv(self.j,'entities'))
if __name__=='__main__':unittest.main()

class PipelineTests(unittest.TestCase):
 def test_search_download_extract_export_without_catalog(self):
  tmp=tempfile.TemporaryDirectory();old=r.DB;r.DB=Path(tmp.name)/'r.sqlite'
  try:
   document=b'<html><p>Alpha Observatory studies astronomy in Jaipur.</p><p>This public institutional directory describes the research facilities and programmes maintained by the observatory.</p></html>'
   calls=[]
   def model(system,user):
    calls.append(system)
    if len(calls)==1:return {'fields':['location'],'entity_types':['observatory'],'search_queries':['observatories Jaipur'],'limit':1}
    return {'records':[{'name':'Alpha Observatory','type':'observatory','attributes':[{'field':'location','value':'Jaipur','quote':'Alpha Observatory studies astronomy in Jaipur.'}]}]}
   e=r.ResearchEngine(model,lambda q:{'results':[{'url':'https://example.org/source','title':'Observatory'}],'search_calls':1},lambda q:None)
   j={'id':'pipeline','query':'Observatories Jaipur','status':'queued','plan':{},'entities':[],'claims':[],'evidence':[],'sources':[],'gaps':[],'metrics':{'model_calls':0,'search_calls':0,'downloaded_sources':0,'rejected_extractions':0}}
   with patch.object(r,'fetch_source',return_value=('https://example.org/source',document,'text/html')),patch.object(r,'BASE',Path(tmp.name)):
    (Path(tmp.name)/'data').mkdir()
    r.ACTIVE.acquire();e.run(j)
   persisted=r.get('pipeline');self.assertEqual(persisted['status'],'complete');self.assertEqual(r.results(persisted)[0]['location'],'Jaipur');self.assertIn('https://example.org/source',r.export_csv(persisted));self.assertEqual(len(persisted['evidence']),1)
  finally:r.DB=old;tmp.cleanup()
 def test_csv_export_union_of_gap_columns(self):
  j={'gaps':[{'reason':'none'},{'source':'a','reason':'failed'}]}
  self.assertIn('reason,source',r.export_csv(j,'gaps'))
