import json,random,re,statistics,time,sys,itertools
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from catalog import connection,metadata,query_catalog,rules_plan
from subscribers import profile,reconcile,demo,load_private
ROOT=Path(__file__).resolve().parents[1]
def tokens(s):return set(re.findall(r'\w+',s.casefold()))
def predict(a,b):
 x,y=tokens(a['name']),tokens(b['name']);score=len(x&y)/max(1,len(x|y))
 distinction=lambda r:('evening' in r['name'].lower(),'morning' in r['name'].lower())
 return score>=.8 and a['state']==b['state'] and a['district']==b['district'] and distinction(a)==distinction(b)
def metrics(pairs,fn):
 tp=fp=fnn=tn=0
 for a,b,label in pairs:
  pred=fn(a,b)
  tp+=bool(pred and label);fp+=bool(pred and not label);fnn+=bool(not pred and label);tn+=bool(not pred and not label)
 return {'true_positive':tp,'false_positive':fp,'false_negative':fnn,'true_negative':tn,'precision':tp/(tp+fp) if tp+fp else None,'recall':tp/(tp+fnn) if tp+fnn else None}
with connection() as c:rows=[dict(r) for r in c.execute('SELECT entity_id,name,state,district,category FROM records')]
groups={}
for r in rows:groups.setdefault(r['entity_id'],[]).append(r)
positive=[(a,b,True) for rs in groups.values() for a,b in itertools.combinations(rs,2)]
# Hard negatives share district and at least one non-generic name token.
block={};negative=[];seen=set();rng=random.Random(17)
for r in rows:
 for t in tokens(r['name'])-{'college','of','and','the','institute','university','government','school','arts','science','education','mahavidyalaya'}:
  key=(r['state'],r['district'],t)
  for b in block.get(key,[])[:8]:
   pair=tuple(sorted([r['entity_id'],b['entity_id']]))
   if r['entity_id']!=b['entity_id'] and pair not in seen:negative.append((r,b,False));seen.add(pair)
  block.setdefault(key,[]).append(r)
rng.shuffle(positive);rng.shuffle(negative);pairs=positive[:500]+negative[:500];rng.shuffle(pairs)
# Candidate detector gets only name/location; labels originate from source AISHE IDs, not an LLM.
masked=[({k:v for k,v in a.items() if k!='entity_id'},{k:v for k,v in b.items() if k!='entity_id'},label) for a,b,label in pairs]
latencies=[];queries=['Find 50 colleges in UP','दिल्ली के 50 कॉलेज दिखाओ','Find 100 universities in India','Find 500 colleges in Maharashtra','Find 50 research institutes in India']
results=[]
for q in queries:
 p=rules_plan(q);timings=[]
 for i in range(5):
  t=time.perf_counter();r=query_catalog(p);timings.append((time.perf_counter()-t)*1000)
 latencies+=timings;results.append({'query':q,'matches':r['total_matches'],'returned':r['returned_entities'],'median_ms':round(statistics.median(timings),2)})
t=time.perf_counter();private=load_private();private_ms=(time.perf_counter()-t)*1000
report={'scope':'Local measured benchmark. Identifier-labelled pairs are a proxy, NOT independently audited identity truth. Same-source-family overlap is often easy. Names/location candidate detector is evaluation-only; production institution auto-linking uses exact AISHE IDs. No LLM grading.','dataset':{'source_rows':len(rows),'unique_aishe_ids':len(groups),'same_id_pairs_available':len(positive),'labelled_pairs':len(masked),'positive_pairs':sum(p[2] for p in masked),'negative_pairs':sum(not p[2] for p in masked),'random_seed':17},'candidate_detector':metrics(masked,predict),'exact_name_baseline':metrics(masked,lambda a,b:a['name'].strip().casefold()==b['name'].strip().casefold()),'performance':{'query_runs':len(latencies),'median_ms':round(statistics.median(latencies),2),'max_ms':round(max(latencies),2),'queries':results,'private_subscriber_rows':private['input_records'],'private_profile_candidate_groups':private['linked_groups'],'private_profile_linked_rows':private['records_in_groups'],'private_reconciliation_ms':round(private_ms,2)},'limitations':['No held-out human-reviewed identity benchmark yet.','No real-world precision claim for subscriber profile associations.','AI/network latency excluded from database timings.','No click, bounce or subscription data; active email cannot be selected.','This is a local prototype, not a multi-user load test.']}
(ROOT/'reports').mkdir(exist_ok=True);(ROOT/'reports'/'benchmark.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
