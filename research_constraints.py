"""Code-owned interpretations and literal checks for explicit numeric requests."""
import re
from datetime import date

def validate_constraints(raw,fields):
 out=[]
 if not isinstance(raw,list):raise ValueError("Research constraints must be an array")
 for c in raw[:12]:
  if not isinstance(c,dict) or c.get("field") not in fields:raise ValueError("Constraint field must exist in the proposed schema")
  t=c.get("type");op=c.get("operator");v=c.get("value")
  allowed={"number":{"gt","gte","lt","lte","eq"},"string":{"contains","eq"},"date":{"gt","gte","lt","lte","eq"}}
  if t not in allowed or op not in allowed[t]:raise ValueError("Unsupported typed comparison")
  if t=="number" and (type(v) not in (int,float)):raise ValueError("Numeric constraint requires a numeric value")
  if t=="date":date.fromisoformat(v)
  if t=="string" and not isinstance(v,str):raise ValueError("Text constraint requires text")
  out.append({k:c[k] for k in ["field","type","operator","value","unit","metric"] if k in c})
 return out

def compare(n,c):
 return {"gt":lambda:n>c["value"],"gte":lambda:n>=c["value"],"lt":lambda:n<c["value"],"lte":lambda:n<=c["value"],"eq":lambda:n==c["value"]}[c["operator"]]()


def enrich(plan,query):
 q=query.lower()
 m=re.search(r'(?:average|avg)[^.;\n]{0,100}?(above|over|greater than|more than|at least|>=|>)\s*[₹]?\s*(\d+(?:\.\d+)?)\s*(?:lakhs?|lacs?|lpa)\b',q)
 if not m:return plan
 fields=['college_name','city','programme','campus','reporting_year','average_package_lpa']
 plan['fields']=list(dict.fromkeys(fields+plan.get('fields',[])))[:12]
 plan['constraints']=[c for c in plan.get('constraints',[]) if c['field'] not in ('average_package_lpa','city')]+[{'field':'average_package_lpa','type':'number','operator':'gte' if m[1] in ['at least','>='] else 'gt','value':float(m[2]),'unit':'INR_lakh_per_annum','metric':'average','evidence_required':True}]
 if re.search(r'\bdelhi\b',q):plan['constraints'].append({'field':'city','type':'string','operator':'contains','value':'Delhi','evidence_required':True})
 plan['interpretation']='Average placement means average annual placement package in INR LPA. Highest, median, internship stipend and overall placement rate cannot substitute. Programme/campus and reporting year stay attached; unspecified year is not assumed current.'
 return plan

def apply(row,claims,evidence,plan):
 checks=[]
 for c in plan.get('constraints',[]):
  field=c['field'];value=str(row.get(field,''));matched=[x for x in claims if x['predicate']==field]
  quotes=' '.join(evidence[x['evidence_id']]['quote'] for x in matched)
  if not value:checks.append({'field':field,'status':'UNKNOWN','reason':'Requested field is absent; other metrics cannot substitute.'});continue
  if c['type']=='string':
   ok=(c['value'].casefold() in value.casefold()) if c['operator']=='contains' else (c['value'].casefold()==value.casefold());checks.append({'field':field,'status':'PASS' if ok else 'FAIL','reason':'Literal source-linked location check.'});continue
  if c['type']=='date':
   try:
    n=date.fromisoformat(value).isoformat();ok=compare(n,c)
    checks.append({'field':field,'status':'PASS' if ok else 'FAIL','reason':'ISO source date compared against requested date.'})
   except (ValueError,TypeError):checks.append({'field':field,'status':'UNKNOWN','reason':'Source date is not an unambiguous ISO date.'})
   continue
  if c.get('unit')!='INR_lakh_per_annum':
   nums=re.findall(r'(?<!\w)\d+(?:\.\d+)?',value.replace(',',''))
   unit=c.get('unit','number');context=value+' '+quotes
   supported=unit=='number' or (unit=='percent' and bool(re.search(r'%|percent',context,re.I))) or (unit=='INR' and bool(re.search(r'₹|INR|Rs\.?',context)))
   if len(nums)!=1 or not supported:
    checks.append({'field':field,'status':'UNKNOWN','reason':'Numeric value or supported unit is not explicit in evidence.'});continue
   n=float(nums[0])
   if unit=='INR':n*=10000000 if re.search(r'crores?',value,re.I) else 100000 if re.search(r'lakhs?|lacs?',value,re.I) else 1
   ok=compare(n,c);checks.append({'field':field,'status':'PASS' if ok else 'FAIL','reason':f"Literal {field} source value {n} {c['operator']} {c['value']} {unit}."});continue
  if re.search(r'\b(?:USD|dollars?|stipend|monthly|per month)\b',value+' '+quotes,re.I):
   checks.append({'field':field,'status':'UNKNOWN','reason':'Currency or period differs from annual INR LPA.'});continue
  unit=re.search(r'\bLPA\b|lakhs?\s*(?:per annum|p\.?a\.?)|lacs?\s*(?:per annum|p\.?a\.?)',value+' '+quotes,re.I)
  metric=c.get('metric') or next((m for m in ['average','median','highest'] if m in field),None)
  avg=(re.search(r'\b(?:average|avg)\b',quotes,re.I) if metric=='average' else re.search(r'\b'+re.escape(metric)+r'\b',quotes,re.I) if metric in ['median','highest'] else True)
  nums=re.findall(r'(?<!\w)\d+(?:\.\d+)?',value.replace(',',''))
  if not unit or not avg or len(nums)!=1:
   checks.append({'field':field,'status':'UNKNOWN','reason':'Need a source-linked average value with explicit annual INR LPA unit; no range or mixed values.'});continue
  n=float(nums[0]);ok=compare(n,c)
  checks.append({'field':field,'status':'PASS' if ok else 'FAIL','value_lpa':n,'reason':f"Literal source claim: {n} LPA {c['operator']} {c['value']} LPA."})
 if checks:
  row['criteria_checks']=checks
  row['criteria_status']='excluded' if any(x['status']=='FAIL' for x in checks) else 'needs_review' if any(x['status']=='UNKNOWN' for x in checks) else 'matched_fields'
  row['criteria_reason']='; '.join(x['reason'] for x in checks)+' Literal checks do not independently certify the source or claim attribution.'
