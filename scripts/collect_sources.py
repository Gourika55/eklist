import concurrent.futures,hashlib,json,re,sys,urllib.request
from pathlib import Path
from urllib.parse import urljoin,urlsplit
from html.parser import HTMLParser
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data'/'sources';OUT.mkdir(parents=True,exist_ok=True)
class Page(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.parts=[];self.anchor=None;self.skip=0
 def handle_starttag(self,t,a):
  d=dict(a)
  if t in ('script','style'):self.skip+=1
  if t=='a':self.anchor=[d.get('href',''),'']
 def handle_endtag(self,t):
  if t=='a' and self.anchor:self.links.append(tuple(self.anchor));self.anchor=None
  if t in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip:self.parts.append(d)
  if self.anchor:self.anchor[1]+=d

def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'EkListResearch/1.0 (institution directory research)'})
 with urllib.request.urlopen(req,timeout=18) as r:
  data=r.read(15000000);return data,r.geturl(),r.headers.get('Content-Type','')
def save(name,url,kind,period=''):
 slug=re.sub('[^a-z0-9]+','-',name.lower()).strip('-')[:75];record={'name':name,'url':url,'kind':kind,'period':period,'retrieved_at':datetime.now(timezone.utc).isoformat(),'reuse':'Publicly accessible; redistribution license not established. Research snapshot, not a blanket reuse grant.'}
 try:
  data,final,ctype=fetch(url);ext='.pdf' if data.startswith(b'%PDF') else '.html'
  if kind=='historical' and ext!='.pdf':raise ValueError('Expected PDF, received a non-PDF response')
  path=OUT/(slug+ext);path.write_bytes(data);record.update(status='downloaded',final_url=final,file=str(path.relative_to(ROOT)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
  if ext=='.html':
   p=Page();p.feed(data.decode('utf-8',errors='replace'));text='\n'.join(x.strip() for x in p.parts if x.strip());(OUT/(slug+'.txt')).write_text(text)
   record['text_file']=str((OUT/(slug+'.txt')).relative_to(ROOT))
   record['email_candidates']=sorted(set(re.findall(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',text)))[:15]
   record['extraction_status']='Regex candidates from page text; not individually verified contacts'
   contacts=[urljoin(final,h) for h,t in p.links if 'contact' in t.lower() and urlsplit(urljoin(final,h)).hostname==urlsplit(final).hostname]
   if kind=='institution' and contacts:
    try:
     body,cu,ct=fetch(contacts[0]);cp=OUT/(slug+'-contact.html');cp.write_bytes(body);record['contact_url']=cu;record['contact_file']=str(cp.relative_to(ROOT));record['contact_sha256']=hashlib.sha256(body).hexdigest()
     parser=Page();parser.feed(body.decode('utf-8',errors='replace'));text='\n'.join(x.strip() for x in parser.parts if x.strip());(OUT/(slug+'-contact.txt')).write_text(text)
     record['email_candidates']=sorted(set(re.findall(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',text)))[:15]
    except Exception as ex:record['contact_error']=type(ex).__name__
 except Exception as ex:record.update(status='failed',error=str(ex)[:160])
 return record

p=Page();html=(Path.home()/'Downloads'/'Colleges at DU - Delhi University.html').read_text();section=html[html.find('Acharya')-160:];section=section[:section.find('Other links')] if 'Other links' in section else section;p.feed(section)
links=[];seen=set()
for h,t in p.links:
 t=' '.join(t.split())
 if not h.startswith(('http://','https://')) or not any(x in t.lower() for x in ['college','mahavidyalaya','miranda']):continue
 if h in seen:continue
 seen.add(h);links.append((t,h.replace('http://','https://',1)))
# Twenty-four different colleges selected in source-directory order, not a representative national sample.
tasks=[(n,u,'institution','') for n,u in links[:24]]+[
 ('DU undergraduate bulletin 2024-25','https://admission.uod.ac.in/2024/userfiles/downloads/28022024_BOI-UG-2024-25_compressed-o.pdf','historical','2024-25'),
 ('DU undergraduate bulletin 2025-26','https://www.du.ac.in/uploads/07032025_UG-BOI_compressed.pdf','historical','2025-26'),
 ('DU hosted college websites','https://ducc.du.ac.in/web-hosting/','directory','')]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(lambda a:save(*a),tasks))
report={'sources':results,'downloaded':sum(r['status']=='downloaded' for r in results),'attempted':len(results),'note':'Historical bulletins are admission publications, not complete institution master registries. They support year-labelled comparisons only. No closure or affiliation change inferred from absence.'}
(ROOT/'data'/'source-packs.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps({'downloaded':report['downloaded'],'attempted':report['attempted'],'sources':[{k:r.get(k) for k in ('name','status','kind','bytes','error')} for r in results]},indent=2))
