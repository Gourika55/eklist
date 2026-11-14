"""Typed, source-reviewed packs. Coverage is disclosed; no model confidence scores."""
import json,re,hashlib
from pathlib import Path
from datetime import date
PACK=Path(__file__).parent/'config/reviewed/pack.json'
def retrieve(query):
 q=query.lower().replace('-', ' ')
 if not PACK.exists():return None
 pack=json.loads(PACK.read_text());kind=None
 if re.search(r'b[ .-]?tech',q) and 'kanpur' in q and re.search(r'fees?|tuition',q):
  # Only the implemented four-year / less-than budget semantics are supported here.
  budget=re.search(r'(?:less than|under|below)\s*(\d+(?:\.\d+)?)\s*(lakh|lac)',q)
  if not budget or not re.search(r'4\s*years?|four\s*years?',q):return None
  if re.search(r'hostel|mess|scholarship|placement|government|private|ranking|accredit',q):return None
  kind='colleges';cap=float(budget[1])*100000
 elif re.search(r'fund(?:ed|ing)',q) and '2026' in q and re.search(r'education|edtech',q) and re.search(r'indian|india',q):
  if re.search(r'less than|more than|under|above|before|after|only.*(?:seed|series)|mumbai|delhi|bengaluru',q):return None
  kind='funding'
 if not kind:return None
 rows=[];seen=set()
 for item in pack[kind]:
  r=dict(item)
  if kind=='colleges':
   if len(r['years'])!=4 or any(type(x)!=int or x<0 for x in r['years']):continue
   total=sum(r['years'])
   if total>=cap:continue
   r.update(year_1_inr=r['years'][0],year_2_inr=r['years'][1],year_3_inr=r['years'][2],year_4_inr=r['years'][3],four_year_academic_fee_inr=total,calculation=' + '.join(map(str,r['years']))+' = '+str(total),criteria_reason='Kanpur + B.Tech + four published yearly amounts + sum below budget. Academic/course fees only.')
   if r.get('branches'):r['branch_fee_totals_inr']=json.dumps({k:sum(v) for k,v in r['branches'].items()});r['branch']='Computer Science shown; branch totals retained'
   key=r['id']
  else:
   d=date.fromisoformat(r['announcement_reported_on'])
   if d.year!=2026:continue
   key=(r['id'],r['announcement_reported_on'],r['amount'],r['currency'])
   r['criteria_reason']='India education company; dated 2026 public funding report; normalized amount and event identity reviewed.'
  if key in seen:continue
  seen.add(key)
  r.update(entity_id=r['id'],entity_type='college' if kind=='colleges' else 'funding_round',criteria_status='source_verified',reviewed_at=pack['reviewed_at'],review_method=pack['review_method'],source_urls=r['source_url'],evidence_ids='reviewed:'+r['id'],missing_fields='',status='Source reviewed')
  for field in ['years','branches','id','download_error']:r.pop(field,None)
  rows.append(r)
 n=re.search(r'(?:find|up to)\s+(\d+)\b',q);limit=min(50,int(n[1])) if n else 50
 return {'rows':rows[:limit],'kind':kind,'requested':limit,'available':len(rows),'reviewed_at':pack['reviewed_at']}

def populate(job,found):
 rows=found['rows'];job['verified_rows']=rows
 excluded={'entity_id','name','entity_type','source_urls','source_url','evidence_ids','missing_fields','status','criteria_status','criteria_reason','evidence','review_method','retrieved_url','download_status','sha256','bytes','locator'}
 fields=[k for r in rows for k in r if k not in excluded]
 job['plan']={'objective':job['query'],'fields':(['course','city','four_year_academic_fee_inr','calculation','fee_scope','branch_fee_totals_inr'] if found['kind']=='colleges' else ['announcement_reported_on','amount','currency','round','investors','date_basis']),'limit':found['requested'],'requirements':'Reviewed source pack; explicit coverage and fee scope.'}
 for r in rows:
  sid='reviewed:'+r['entity_id'];job['sources'].append({'id':sid,'url':r['source_url'],'title':r['name'],'sha256':r.get('sha256',''),'retrieved_at':found['reviewed_at']})
  job['entities'].append({'id':r['entity_id'],'name':r['name'],'type':r['entity_type']})
  job['evidence'].append({'id':sid,'claim_id':sid,'source_id':sid,'source_url':r['source_url'],'quote':r['evidence'],'locator':r['locator']+'; reviewer transcription, not a contiguous quotation','retrieved_at':found['reviewed_at']})
  job['claims'].append({'id':sid,'subject_id':r['entity_id'],'predicate':'reviewed_source_record','value':r['evidence'],'object_id':None,'evidence_id':sid,'review_status':'source_reviewed'})
 job['status']='complete';job['stage']=f"{len(rows)} source-verified rows ready · reviewed pack"
 job['notice']=f"Reviewed source pack checked {found['reviewed_at']}. {len(rows)} verified matches from this pack; requested up to {found['requested']}. Coverage is not exhaustive. Fee totals cover published academic/course fees; hostel, mess and unlisted charges are excluded. Funding dates mean the dated announcement/report, not transaction closing. No rows invented to meet the target."
 if len(rows)<found['requested']:job['gaps'].append({'reason':f"Coverage shortfall: {found['requested']-len(rows)} requested rows not established by this reviewed pack."})
