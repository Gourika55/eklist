import unittest
from research_constraints import enrich,apply
class PlacementSchemaTests(unittest.TestCase):
 def plan(self):return enrich({'fields':[]},'find tech colleges in delhi average placement should be above 10 lakhs')
 def row(self,value,city='Delhi',quote='Example College in Delhi reports average package 12 LPA.'):
  r={'average_package_lpa':value,'city':city};cs=[{'predicate':'average_package_lpa','evidence_id':'e'},{'predicate':'city','evidence_id':'e'}]
  apply(r,cs,{'e':{'quote':quote}},self.plan());return r
 def test_exact_query_schema(self):
  p=self.plan();self.assertIn('average_package_lpa',p['fields']);self.assertIn('reporting_year',p['fields']);self.assertEqual(p['constraints'][0]['operator'],'gt');self.assertEqual(p['constraints'][0]['value'],10)
 def test_strict_threshold(self):
  self.assertEqual(self.row('12 LPA')['criteria_status'],'matched_fields')
  self.assertEqual(self.row('10 LPA')['criteria_status'],'excluded')
 def test_highest_cannot_substitute(self):
  self.assertEqual(self.row('50 LPA',quote='Example College in Delhi reports highest package 50 LPA.')['criteria_status'],'needs_review')
 def test_other_currency_and_period(self):
  self.assertEqual(self.row('12 LPA',quote='Average USD salary 12 LPA.')['criteria_status'],'needs_review')
  self.assertEqual(self.row('12',quote='Average stipend 12 monthly.')['criteria_status'],'needs_review')
 def test_missing_average_stays_unknown(self):
  self.assertEqual(self.row('')['criteria_status'],'needs_review')
 def test_wrong_city_excluded(self):
  self.assertEqual(self.row('12 LPA',city='Kanpur')['criteria_status'],'excluded')

class GeneralConstraintTests(unittest.TestCase):
 def test_dynamic_numeric_and_date_fields(self):
  from research_constraints import validate_constraints
  constraints=validate_constraints([{'field':'award_amount','type':'number','operator':'gte','value':50000,'unit':'INR'},{'field':'announcement_date','type':'date','operator':'gte','value':'2026-01-01'}],['award_amount','announcement_date'])
  row={'award_amount':'INR 60000','announcement_date':'2026-06-01'}
  claims=[{'predicate':k,'evidence_id':'e'} for k in row]
  apply(row,claims,{'e':{'quote':'Example reports INR 60000 on 2026-06-01.'}},{'constraints':constraints})
  self.assertEqual(row['criteria_status'],'matched_fields')
 def test_unknown_model_field_rejected(self):
  from research_constraints import validate_constraints
  with self.assertRaises(ValueError):validate_constraints([{'field':'invented','type':'number','operator':'gt','value':1}],['amount'])
