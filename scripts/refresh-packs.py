"""Refresh registered public packs; uses configured NVIDIA credentials. No private inputs."""
import sys,json,argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import packs
from server import research_llm
parser=argparse.ArgumentParser();parser.add_argument('--category',choices=list(packs.CATEGORIES));parser.add_argument('--force',action='store_true');args=parser.parse_args()
entries=json.loads((packs.BASE/'config'/'opportunity-packs.json').read_text())
if args.category:entries=[e for e in entries if e['category']==args.category]
with ThreadPoolExecutor(max_workers=3) as pool:
 futures=[pool.submit(packs.collect,e,research_llm,args.force) for e in entries]
 for future in as_completed(futures):
  s=future.result();print(json.dumps({k:s.get(k) for k in ['title','status','records','rejected_extractions','error','cached']},ensure_ascii=False),flush=True)
print(json.dumps({'clusters':packs.overview()['clusters']},indent=2))
