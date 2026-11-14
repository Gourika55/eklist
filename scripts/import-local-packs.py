"""Import hash-verified local public snapshots without downloading them again."""
import sys,json,argparse,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import packs
from server import research_llm
p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--root',required=True);p.add_argument('--audit-only',action='store_true');a=p.parse_args()
root=Path(a.root).resolve();manifest=json.loads(Path(a.manifest).read_text());entries=[];audit=[]
for s in manifest['downloaded_sources']:
 if s.get('status')!='downloaded':continue
 path=(root/s['file']).resolve()
 if not path.is_relative_to(root):raise ValueError('Snapshot outside corpus root')
 body=path.read_bytes();valid=hashlib.sha256(body).hexdigest()==s['sha256']
 text=packs.parse_source(body,s.get('mime','text/plain'),s['url']) if valid else ''
 row={'id':s['id'],'hash_valid':valid,'characters':len(text),'usable':valid and len(text)>=100};audit.append(row)
 if not row['usable']:continue
 category={'education':'education','research_innovation':'research','organisations':'ngo','opportunities':'scholarships'}[s['pack']]
 if 'hackclub' in s['id']:category='events'
 entries.append({'category':category,'url':s['url'],'title':s['publisher']+' — '+s['id'],'local_snapshot':str(path),'expected_sha256':s['sha256'],'retrieved_at':s['retrieved_at'],'mime':s.get('mime','text/plain')})
print(json.dumps({'audit':audit,'usable_sources':len(entries)},indent=2),flush=True)
if not a.audit_only:
 with ThreadPoolExecutor(max_workers=3) as pool:
  for s in pool.map(lambda e:packs.collect(e,research_llm),entries):print(json.dumps({k:s.get(k) for k in ('title','status','records','error')},ensure_ascii=False),flush=True)
