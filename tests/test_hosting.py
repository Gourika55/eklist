import gzip,hashlib,os,sqlite3,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from hosting import authorized,validate_hosting
from bootstrap_catalog import install_archive
class HostingTests(unittest.TestCase):
 def test_hosted_requires_secret(self):
  with patch.dict(os.environ,{'EKLIST_HOSTED':'1','EKLIST_BACKEND_TOKEN':''}):
   self.assertFalse(authorized({'Host':'localhost'}))
   with self.assertRaises(RuntimeError):validate_hosting()
 def test_token_not_origin_grants_access(self):
  with patch.dict(os.environ,{'EKLIST_HOSTED':'1','EKLIST_BACKEND_TOKEN':'x'*32}):
   self.assertTrue(authorized({'Authorization':'Bearer '+'x'*32}))
   self.assertFalse(authorized({'Origin':'https://myapp.vercel.app'}))
 def test_local_origin_retained(self):
  with patch.dict(os.environ,{'EKLIST_HOSTED':'0'}):
   self.assertTrue(authorized({'Host':'localhost:4174'}))
   self.assertFalse(authorized({'Host':'localhost:4174','Origin':'https://evil.example'}))
 def test_failed_seed_preserves_existing_file(self):
  with tempfile.TemporaryDirectory() as d:
   a=Path(d)/'archive.gz';a.write_bytes(gzip.compress(b'not a database'));target=Path(d)/'db';target.write_bytes(b'existing')
   with self.assertRaises(ValueError):install_archive(a,target,'0'*64)
   self.assertEqual(target.read_bytes(),b'existing')
