import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
import packs,bootstrap_packs
class SeedTest(unittest.TestCase):
 def test_bundled_library_restores_eighty_once(self):
  with tempfile.TemporaryDirectory() as d,patch.object(packs,'DB',Path(d)/'packs.sqlite'):
   self.assertEqual(bootstrap_packs.restore(),80)
   self.assertEqual(bootstrap_packs.restore(),0)
   self.assertEqual(packs.search()['total'],80)
   self.assertTrue(all(r['source_sha256'] and r['identity_quote'] for r in packs.search()['records']))
