import unittest
from catalog import rules_plan,query_catalog,validate_plan,metadata
from subscribers import profile,reconcile,demo
class BackendTests(unittest.TestCase):
 def test_national_import(self):self.assertEqual(metadata()['raw_records'],74847)
 def test_up_request(self):
  p=rules_plan('Find 50 colleges in UP');self.assertEqual(p['state'],'Uttar Pradesh');r=query_catalog(p);self.assertEqual(r['returned_entities'],50);self.assertTrue(all(x['state']=='Uttar Pradesh' for x in r['records']))
 def test_hindi_count(self):self.assertEqual(rules_plan('दिल्ली के २५ कॉलेज दिखाओ')['limit'],25)
 def test_unknown_state(self):
  with self.assertRaises(ValueError):validate_plan({'category':'college','state':'Atlantis'})
 def test_invalid_limit(self):
  with self.assertRaises(ValueError):validate_plan({'category':'college','limit':-1})
 def test_linkage_evidence(self):
  r=query_catalog({'category':'vidyalaxmi','limit':100});self.assertTrue(all(x['source_row']>3 and x['original'] for x in r['records']));self.assertLessEqual(len(set(x['entity_id'] for x in r['records'])),100)
 def test_profile_urls(self):self.assertEqual(profile('https://in.linkedin.com/in/Person/?trk=a','linkedin'),profile('https://www.linkedin.com/in/person','linkedin'))
 def test_not_company_profile(self):self.assertEqual(profile('https://linkedin.com/company/shared','linkedin'),'')
 def test_bad_host(self):self.assertEqual(profile('https://linkedin.com.evil.test/in/person','linkedin'),'')
 def test_country_not_blocker(self):self.assertEqual(demo()['groups'][0]['records'].__len__(),3)
 def test_no_name_only_link(self):self.assertEqual(reconcile([{'First Name':'Same'},{'First Name':'Same'}])['linked_groups'],0)
 def test_no_active_email_inference(self):self.assertIsNone(demo()['groups'][0]['preferred_email'])
if __name__=='__main__':unittest.main()

class SubscriberImportTests(unittest.TestCase):
 def test_csv_column_mapping_and_no_data_loss(self):
  from subscribers import import_csv
  result=import_csv('mail,full,profile\na@example.com,A Person,https://linkedin.com/in/demo-one\nb@example.com,A P,https://in.linkedin.com/in/demo-one/\nc@example.com,A Person,https://linkedin.com/in/demo-two',{'Email':'mail','First Name':'full','Linkedin':'profile'})
  self.assertEqual(result['input_records'],3);self.assertEqual(result['linked_groups'],1);self.assertEqual(len(result['records']),3)
 def test_missing_email_mapping(self):
  from subscribers import import_csv
  with self.assertRaises(ValueError):import_csv('name,role\nA,Editor')
 def test_invalid_csv_row(self):
  from subscribers import import_csv
  with self.assertRaises(ValueError):import_csv('Email,Linkedin\na@example.com')
