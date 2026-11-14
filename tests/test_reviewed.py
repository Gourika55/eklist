import unittest
from reviewed import retrieve
class ReviewedChecks(unittest.TestCase):
 def test_four_year_fees_and_unique_colleges(self):
  r=retrieve('Find 50 btech colleges in kanpur that have fees less than 10 lakh for 4 years')['rows']
  self.assertEqual(len(r),2);self.assertEqual(len({x['entity_id'] for x in r}),2)
  self.assertEqual(r[0]['four_year_academic_fee_inr'],517500)
  self.assertTrue(all(x['four_year_academic_fee_inr']<1000000 for x in r))
 def test_fee_wording_variation(self):
  self.assertEqual(len(retrieve('List BTech colleges in Kanpur whose four-year academic fees are below 10 lakh.')['rows']),2)
 def test_year_and_funding_event_identity(self):
  r=retrieve('Find Indian education startups funded in 2026')['rows']
  self.assertEqual(len(r),5);self.assertEqual(len({x['entity_id'] for x in r}),5)
  self.assertTrue(all(x['announcement_reported_on'].startswith('2026-') for x in r))
 def test_unsupported_scope_does_not_use_pack(self):
  self.assertIsNone(retrieve('Find colleges in Mumbai'))
  self.assertIsNone(retrieve('Find Indian education startups funded in 2025'))
