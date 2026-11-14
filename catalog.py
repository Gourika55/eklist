import json,re,sqlite3,time
from urllib.parse import urlsplit
from pathlib import Path
from functools import lru_cache
from ingest import DB
ALIASES={'up':'Uttar Pradesh','उत्तर प्रदेश':'Uttar Pradesh','दिल्ली':'Delhi','delhi':'Delhi','महाराष्ट्र':'Maharashtra','बिहार':'Bihar','कर्नाटक':'Karnataka','राजस्थान':'Rajasthan','पंजाब':'Punjab','गुजरात':'Gujarat','mp':'Madhya Pradesh','मध्य प्रदेश':'Madhya Pradesh','तमिलनाडु':'Tamil Nadu','पश्चिम बंगाल':'West Bengal'}
def connection():
    c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;return c
def hostname(v):
    try:return (urlsplit(v if '://' in v else 'https://'+v).hostname or '').lower().removeprefix('www.')
    except ValueError:return ''
@lru_cache(maxsize=1)
def evidence_index():
    p=Path(__file__).resolve().parent/'data'/'source-packs.json'
    if not p.exists():return {}
    domains={}
    with connection() as c:
        for row in c.execute("SELECT entity_id,website FROM records WHERE website<>''"):
            h=hostname(row['website'])
            if h:domains.setdefault(h,set()).add(row['entity_id'])
    mapped={}
    for s in json.loads(p.read_text())['sources']:
        if s['status']!='downloaded' or s['kind']!='institution':continue
        ids=domains.get(hostname(s.get('final_url',s['url'])),set())
        if len(ids)==1:mapped.setdefault(next(iter(ids)),[]).append(s)
    return mapped
def metadata():
    with connection() as c:
        return {'raw_records':c.execute('SELECT count(*) FROM records').fetchone()[0],'entities':c.execute('SELECT count(DISTINCT entity_id) FROM records').fetchone()[0],'sources':[dict(r) for r in c.execute('SELECT * FROM sources')],'states':[r[0] for r in c.execute('SELECT DISTINCT state FROM records ORDER BY state')],'districts':[r[0] for r in c.execute('SELECT DISTINCT district FROM records ORDER BY district')],'categories':['college','university','standalone','research','vidyalaxmi']}
def rules_plan(query,meta=None):
    meta=meta or metadata();q=query.lower();q=re.sub('[०-९]',lambda m:str(ord(m[0])-ord('०')),q)
    category='college' if re.search(r'colleges?|महाविद्यालय|कॉलेज',q) else 'university' if re.search(r'universit|विश्वविद्यालय',q) else 'standalone' if re.search(r'standalone|polytechnic|पॉलिटेक्निक',q) else 'research' if re.search(r'research|r\s*&\s*d|अनुसंधान',q) else 'vidyalaxmi' if re.search(r'vidya.?la[kx]shmi|vidyalaxmi|विद्यालक्ष्मी',q) else None
    state=next((s for s in sorted(meta['states'],key=len,reverse=True) if s.lower() in q),None)
    if not state:state=next((s for a,s in ALIASES.items() if re.search(r'(?<!\w)'+re.escape(a)+r'(?!\w)',q)),None)
    district=next((s for s in sorted(meta['districts'],key=len,reverse=True) if len(s)>2 and s.lower() in q),None)
    num=re.search(r'\b(\d{1,5})\b',q);limit=int(num[1]) if num else 50
    if not category:raise ValueError('Specify colleges, universities, standalone institutions, research institutes or Vidyalaxmi institutions.')
    return validate_plan({'category':category,'state':state,'district':district,'limit':limit,'website_required':bool(re.search(r'with (?:official )?websites?|वेबसाइट सहित',q)),'management':'government' if re.search(r'government|सरकारी',q) else 'private' if re.search(r'private|निजी',q) else None,'name_contains':None},meta)
def validate_plan(p,meta=None):
    meta=meta or metadata()
    if not isinstance(p,dict):raise ValueError('Planner did not return an object.')
    if p.get('category') not in meta['categories']:raise ValueError('Unsupported institution category.')
    for field,allowed in [('state',meta['states']),('district',meta['districts'])]:
        value=p.get(field)
        if value:
            value=next((v for v in allowed if v.lower()==str(value).lower()),None)
            if value is None:raise ValueError('Unknown '+field+'; use an official state or district name.')
        p[field]=value
    if type(p.get('limit',50)) is not int or not 1<=p.get('limit',50)<=500:raise ValueError('Choose 1–500 records per result; the full database remains searchable.')
    if p.get('management') not in (None,'government','private'):raise ValueError('Unsupported management filter.')
    if p.get('website_required') is None:p['website_required']=False
    if type(p.get('website_required',False)) is not bool:raise ValueError('Invalid website filter.')
    name=p.get('name_contains')
    if name is not None and (not isinstance(name,str) or len(name)>100):raise ValueError('Invalid name filter.')
    return {k:p.get(k,d) for k,d in [('category',None),('state',None),('district',None),('limit',50),('website_required',False),('management',None),('name_contains',None)]}
def query_catalog(plan):
    start=time.perf_counter();p=validate_plan(plan);where=['category=?'];args=[p['category']]
    for f in ['state','district']:
        if p[f]:where.append(f+'=?');args.append(p[f])
    if p['website_required']:where.append("website<>''")
    if p['management']:
        where.append('management LIKE ?');args.append('%'+('Government' if p['management']=='government' else 'Private')+'%')
        if p['management']=='government':where.append("management NOT LIKE '%Private%'")
    if p['name_contains']:where.append('instr(lower(name),lower(?))>0');args.append(p['name_contains'])
    clause=' AND '.join(where)
    with connection() as c:
        total=c.execute('SELECT COUNT(DISTINCT entity_id) FROM records WHERE '+clause,args).fetchone()[0]
        ids=[r[0] for r in c.execute('SELECT entity_id FROM records WHERE '+clause+' GROUP BY entity_id ORDER BY MIN(name) COLLATE NOCASE,entity_id LIMIT ?',args+[p['limit']])]
        records=[]
        if ids:
            for r in c.execute('SELECT * FROM records WHERE entity_id IN ('+','.join('?' for _ in ids)+') ORDER BY name COLLATE NOCASE,source_row',ids):
                d=dict(r);d['original']=json.loads(d['original']);d['supporting_evidence']=evidence_index().get(d['entity_id'],[]);records.append(d)
        sources=[dict(r) for r in c.execute('SELECT * FROM sources')]
    return {'plan':p,'total_matches':total,'returned_entities':len(ids),'truncated':total>len(ids),'shortfall':max(0,p['limit']-total),'records':records,'sources':sources,'query_ms':round((time.perf_counter()-start)*1000,2),'ordering':'Alphabetical name, then AISHE code. Not a ranking.','matching_policy':'Exact AISHE-code linkage; conflicting fields retained. No fuzzy automatic merges.','network_calls':0}
