"""Live smoke test; requires a configured site and incurs public-research API calls."""
import base64,json,os,time,urllib.request,urllib.error,csv,io
site=os.environ['EKLIST_SITE_URL'].rstrip('/')
auth='Basic '+base64.b64encode((os.environ['EKLIST_DEMO_USER']+':'+os.environ['EKLIST_DEMO_PASSWORD']).encode()).decode()
def call(path,data=None,authenticated=True):
 h={'Content-Type':'application/json'}
 if authenticated:h['Authorization']=auth
 req=urllib.request.Request(site+path,data=json.dumps(data).encode() if data is not None else None,headers=h)
 with urllib.request.urlopen(req,timeout=65) as r:return r.read(),r.headers
try:call('/api/catalog',authenticated=False);raise AssertionError('Unauthenticated API access allowed')
except urllib.error.HTTPError as e:assert e.code==401,e.code
health=json.loads(call('/api/health')[0]);assert health['database'] and health['ai'] and health['serper'],health
r=json.loads(call('/api/query',{'query':'उत्तर प्रदेश के 50 कॉलेज दिखाओ','ai':False})[0]);assert r['returned_entities']==50
assert all(x['state']=='Uttar Pradesh' for x in r['records'])
s=json.loads(call('/api/subscribers/import',{'csv':'Email,First Name\ndemo@example.com,Demo'})[0]);assert s['input_records']==1
j=json.loads(call('/api/research/jobs',{'query':'Identify the NISAR mission and its NASA and ISRO development organisations from official NASA or ISRO sources.'})[0]);id=j['id']
for _ in range(100):
 j=json.loads(call('/api/research/jobs/'+id)[0])
 if j['status'] not in ('pending','queued','running'):break
 time.sleep(3)
raw,headers=call('/api/research/jobs/'+id+'?export=results');assert 'text/csv' in headers['Content-Type']
rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))));assert rows,('No research results',j.get('status'),j.get('error'))
print(json.dumps({'catalogue_rows':health['records'],'query_rows':r['returned_entities'],'research_status':j['status'],'research_rows':len(rows),'csv_bytes':len(raw),'authenticated':True},indent=2))
