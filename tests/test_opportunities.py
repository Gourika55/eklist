import unittest
from datetime import datetime,timezone
import opportunities as o
class OpportunityTests(unittest.TestCase):
 def p(self,kind='jobs',**kw):return o.plan_checked({'kind':kind,**kw},kind)
 def row(self,kind='jobs',**f):
  r=o.newrow(kind,'Engineer','https://example.com/listing');r['fields']=f;return r
 def test_remote_not_global(self):
  r=o.qualify(self.row(mode='remote',geography='USA',open_status='explicitly_open'),self.p(country='India'));self.assertEqual(r['status'],'excluded')
 def test_worldwide_paid(self):
  r=o.qualify(self.row(mode='remote',geography='Worldwide',salary='$20/hour',open_status='explicitly_open'),self.p(country='India',paid=True));self.assertEqual(r['status'],'qualified')
 def test_apac_unknown(self):
  r=o.qualify(self.row(mode='remote',geography='APAC',open_status='explicitly_open'),self.p(country='India'));self.assertEqual(r['status'],'needs_verification')
 def test_missing_salary_unknown(self):
  r=o.qualify(self.row(mode='remote',open_status='explicitly_open'),self.p(paid=True));self.assertEqual(r['status'],'needs_verification')
 def test_geographic_contradiction(self):
  r=o.qualify(self.row(mode='remote',geography='Worldwide',open_status='explicitly_open',description='You must reside in the United States.'),self.p(country='India'));self.assertEqual(r['status'],'needs_verification')
 def test_missing_open_not_inferred(self):self.assertEqual(o.qualify(self.row(mode='remote'),self.p())['status'],'needs_verification')
 def test_deadline_timezone(self):
  self.assertEqual(o.parse_instant('November 14, 2026 at 11:45pm PST').isoformat(),'2026-11-15T07:45:00+00:00');self.assertIsNone(o.parse_instant('November 14, 2026'));self.assertIsNone(o.parse_instant('2026-11-14T23:45:00'))
 def test_submission_not_registration(self):
  r=self.row('hackathons',submission_deadline='2026-12-01T00:00:00Z',open_status='explicitly_open');o.qualify(r,self.p('hackathons',days=30,deadline_kind='registration'),datetime(2026,11,14,tzinfo=timezone.utc));self.assertEqual(r['status'],'needs_verification')
 def test_expired_excluded(self):
  r=self.row('hackathons',registration_deadline='2026-11-01T00:00:00Z',open_status='explicitly_open');o.qualify(r,self.p('hackathons',days=30),datetime(2026,11,14,tzinfo=timezone.utc));self.assertEqual(r['status'],'excluded')
 def test_age(self):
  r=self.row('hackathons',eligibility='Students ages 13 to 18 only',open_status='explicitly_open');o.qualify(r,self.p('hackathons',age=20));self.assertEqual(r['status'],'excluded')
 def test_unspecified_age_unknown(self):
  r=self.row('hackathons',eligibility='Students aged 13 or older',open_status='explicitly_open');o.qualify(r,self.p('hackathons'));self.assertEqual(r['status'],'needs_verification')
 def test_country_exceptions_not_assumed(self):
  r=self.row('hackathons',geography='All countries excluding standard exceptions',open_status='explicitly_open');o.qualify(r,self.p('hackathons',country='India'));self.assertEqual(r['status'],'needs_verification')
 def test_tracking_duplicate(self):
  a=self.row();b=self.row();b['url']+='?utm_source=test';rs,ledger=o.dedupe([a,b]);self.assertEqual(len(rs),1);self.assertEqual(len(ledger),1)
 def test_editions_separate(self):
  a=self.row('hackathons',start_date='2026-11-01T00:00:00Z');b=self.row('hackathons',start_date='2027-11-01T00:00:00Z');rs,_=o.dedupe([a,b]);self.assertEqual(len(rs),2);self.assertNotEqual(rs[0]['id'],rs[1]['id'])
 def test_same_name_different_urls_not_merged(self):
  a=self.row();b=self.row();b['url']='https://example.com/other';self.assertEqual(len(o.dedupe([a,b])[0]),2)
 def test_unsupported_not_dropped(self):
  r=o.qualify(self.row(mode='remote',open_status='explicitly_open'),self.p(unsupported=['experience under 2 years']));self.assertEqual(r['status'],'needs_verification')
 def test_unsafe_export(self):
  j={'rows':[dict(self.row(),title='=HYPERLINK("bad")')],'duplicates':[],'gaps':[]};self.assertIn("'=HYPERLINK",o.csv_export(j,'all'))
 def test_plan_validation(self):
  with self.assertRaises(ValueError):self.p(days=-1)
  with self.assertRaises(ValueError):self.p(paid='yes')
 def test_microdata(self):
  p=o.EventHTML();p.feed('<div itemscope itemtype="https://schema.org/Event"><span itemprop="name">Hack</span><meta itemprop="startDate" content="2026-12-01T00:00:00Z"><a itemprop="url" href="https://example.org">Go</a></div>');self.assertEqual(p.events[0]['name'],'Hack');self.assertEqual(p.events[0]['url'],'https://example.org')
 def test_unicode_age_range(self):
  r=self.row('hackathons',eligibility='ages 13–18',open_status='explicitly_open');o.qualify(r,self.p('hackathons',age=20));self.assertEqual(r['status'],'excluded')
 def test_date_only_long_expired(self):
  r=self.row('hackathons',registration_deadline='2026-05-02',open_status='explicitly_open');o.qualify(r,self.p('hackathons',days=30),datetime(2026,11,14,tzinfo=timezone.utc));self.assertEqual(r['status'],'excluded')
 def test_date_only_boundary_unknown(self):
  r=self.row('hackathons',registration_deadline='2026-11-14',open_status='explicitly_open');o.qualify(r,self.p('hackathons',days=30),datetime(2026,11,14,tzinfo=timezone.utc));self.assertEqual(r['status'],'needs_verification')
 def test_null_optional_fields(self):self.assertFalse(self.p(paid=None,internship=None)['paid'])
 def test_payment_caveat(self):
  r=o.qualify(self.row(mode='remote',open_status='explicitly_open',description='Some tasks may require payment.'),self.p());self.assertEqual(r['status'],'needs_verification')
 def test_filtered_csv(self):
  a=self.row();a['title']='Python Engineer';b=self.row();b['title']='Office Assistant';j={'rows':[a,b],'duplicates':[],'gaps':[]};out=o.csv_export(j,'all','Python');self.assertIn('Python Engineer',out);self.assertNotIn('Office Assistant',out)
