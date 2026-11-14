import unittest,tempfile,hashlib
from pathlib import Path
from unittest.mock import patch
import packs
class PacksTest(unittest.TestCase):
 def test_local_hash_rejection_never_calls_model(self):
  with tempfile.TemporaryDirectory() as d,patch.object(packs,'DB',Path(d)/'db'):
   f=Path(d)/'source';f.write_text('tampered')
   r=packs.collect({'url':'https://example.org','title':'Test','category':'research','local_snapshot':str(f),'expected_sha256':'bad','retrieved_at':packs.now()},lambda *a:self.fail('Model called'))
   self.assertEqual(r['status'],'failed');self.assertIn('SHA-256',r['error'])
 def test_local_import_is_idempotent_and_preserves_date(self):
  with tempfile.TemporaryDirectory() as d,patch.object(packs,'DB',Path(d)/'db'),patch.object(packs,'SNAPSHOTS',Path(d)/'snap'):
   text='Example Institute offers research placements. '*4;f=Path(d)/'source';f.write_text(text)
   entry={'url':'https://example.org','title':'Test','category':'research','local_snapshot':str(f),'expected_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'retrieved_at':'2026-01-01T00:00:00+00:00'}
   model=lambda *a:{'records':[{'name':'Example Institute','identity_quote':'Example Institute offers research placements.','kind':'organisation'}]}
   for _ in range(2):self.assertEqual(packs.collect(entry,model,True)['records'],1)
   result=packs.search();self.assertEqual(result['total'],1);self.assertEqual(result['records'][0]['checked_at'],entry['retrieved_at'])
   self.assertIn('identity_quote',packs.csv_export(result))
   with self.assertRaises(ValueError):packs.csv_export(result,commercial=True)
 def test_unquoted_claim_rejected(self):
  records,rejected=packs.accept_records({'id':'s','url':'https://example.org','category':'research'},'Example Institute offers research placements.',{'records':[{'name':'Example Institute','identity_quote':'Example Institute offers research placements.','attributes':[{'field':'deadline','value':'2026-12-01','quote':'invented deadline 2026-12-01'}]}]})
  self.assertEqual(rejected,1);self.assertEqual(records[0]['attributes'],{})
 def test_unknown_criteria_never_match(self):
  r={'name':'Institute','kind':'organisation','attributes':{},'evidence':[]}
  result=packs.match(r,packs.validate_plan({'category':'research','filters':[{'field':'deadline','operator':'date_from','value':'2026-11-14'}]}))
  self.assertEqual(result['match_status'],'needs_review')
if __name__=='__main__':unittest.main()
