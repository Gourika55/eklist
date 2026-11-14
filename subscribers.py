"""Exact-profile association candidates. No network requests, no name-only merges."""
import csv,json,re,io,os
from urllib.parse import urlsplit,unquote
from pathlib import Path

def profile(value,platform):
    value=str(value or '').strip()
    if not value:return ''
    try:
        u=urlsplit(value if '://' in value else 'https://'+value);host=(u.hostname or '').lower();path=unquote(u.path).strip('/').lower()
        if platform=='linkedin' and (host=='linkedin.com' or host.endswith('.linkedin.com')) and re.fullmatch(r'in/[a-z0-9_%.-]+',path):return 'linkedin.com/'+path
        if platform=='x' and host in ('x.com','www.x.com','twitter.com','www.twitter.com') and re.fullmatch(r'[a-z0-9_]{1,15}',path) and path not in ('home','intent','search','share','login','i'):return 'x.com/'+path
    except ValueError:pass
    return ''

def reconcile(rows):
    parents=list(range(len(rows))); evidence=[];seen={}
    def root(i):
        while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
        return i
    for i,r in enumerate(rows):
        for field,platform in [('Linkedin','linkedin'),('Twitter/X','x')]:
            key=profile(r.get(field),platform)
            if not key:continue
            if key in seen:
                j=seen[key];parents[root(i)]=root(j);evidence.append({'left':j+2,'right':i+2,'field':field,'normalized_profile':key})
            else:seen[key]=i
    groups={}
    for i,r in enumerate(rows):groups.setdefault(root(i),[]).append({'row':i+2,**r})
    linked=[]
    for rs in groups.values():
        if len(rs)<2:continue
        ids={r['row'] for r in rs}
        linked.append({'id':f'person-candidate-{min(ids)}','name':' '.join(rs[0].get(k,'') for k in ['First Name','Last Name']).strip() or 'Unnamed contact','records':rs,'emails':list(dict.fromkeys(r.get('Email','') for r in rs if r.get('Email'))),'evidence':[x for x in evidence if x['left'] in ids and x['right'] in ids],'status':'shared-profile association; identity not independently verified','preferred_email':None})
    return {'input_records':len(rows),'linked_groups':len(linked),'records_in_groups':sum(len(g['records']) for g in linked),'groups':linked,'note':'Profile associations may originate from enrichment and need review. Country is not a blocker. Original values preserved; no country resolution. No activity or consent is inferred.'}

def load_private():
    p=Path(os.environ.get('EKLIST_PRIVATE_CONTACTS_PATH') or str(Path(__file__).parent/'private'/'contacts.csv'))
    with p.open(encoding='utf-8-sig') as f:return reconcile(list(csv.DictReader(f)))

def import_csv(text,mapping=None):
    reader=csv.DictReader(io.StringIO(text.lstrip('\ufeff')));headers=reader.fieldnames or []
    if not headers or len(headers)!=len(set(headers)):raise ValueError('CSV needs unique column headers.')
    aliases={'Email':['email','email address','email_address'],'First Name':['first name','first_name','firstname','name','full name'],'Last Name':['last name','last_name','lastname'],'Linkedin':['linkedin','linkedin url','linkedin_url','linkedin profile'],'Twitter/X':['twitter/x','twitter','x','twitter_url','x_url'],'Company':['company','organization','organisation'],'Role':['role','job title','title'],'Country':['country']}
    mapping=mapping or {};mapped={}
    for target,options in aliases.items():
        selected=mapping.get(target) or next((h for h in headers if h.strip().lower() in options),None)
        if selected and selected not in headers:raise ValueError('Mapped column not found: '+selected)
        if selected:mapped[target]=selected
    if 'Email' not in mapped:raise ValueError('Map an Email column before importing.')
    rows=[]
    for index,r in enumerate(reader):
        if index>=50000:raise ValueError('Limit this prototype to 50,000 subscriber rows per import.')
        if None in r or any(v is None for v in r.values()):raise ValueError('CSV row '+str(index+2)+' has an inconsistent number of columns.')
        rows.append({**{k:r.get(v,'').strip() for k,v in mapped.items()},'Original fields':r})
    result=reconcile(rows);result.update({'imported':True,'mapping':mapped,'records':rows,'synthetic':False})
    return result

def demo():
    # Fictional fixture: no personal contact values copied from the private file.
    rows=[{'First Name':'Aarav','Last Name':'Mehta','Email':'aarav.personal@example.com','Linkedin':'https://in.linkedin.com/in/eklist-demo-person','Twitter/X':'https://x.com/eklistdemo','Country':'India'},
          {'First Name':'A','Last Name':'Mehta','Email':'aarav.work@example.org','Linkedin':'https://www.linkedin.com/in/eklist-demo-person/','Twitter/X':'https://twitter.com/eklistdemo','Country':'United Kingdom'},
          {'First Name':'Aarav','Last Name':'Mehta','Email':'aarav.archive@example.net','Linkedin':'https://linkedin.com/in/eklist-demo-person?trk=test'},
          {'First Name':'Aarav','Last Name':'Mehta','Email':'another.person@example.com','Linkedin':'https://linkedin.com/in/eklist-demo-other'}]
    result=reconcile(rows);result['synthetic']=True;return result
