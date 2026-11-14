"""Repeatable local-only import. Original workbooks are never modified."""
import csv, hashlib, json, re, sqlite3, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from datetime import datetime, timezone

BASE=Path(__file__).resolve().parent
DB=BASE/'data'/'eklist.sqlite'
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
FILES=[('College-ALL COLLEGE.xlsx','college'),('University-ALL UNIVERSITIES.xlsx','university'),('Standalone-ALL STANDALONE.xlsx','standalone'),('R & D Institutes.xlsx','research'),('vidya_lakshmiAll.xlsx','vidyalaxmi')]

def xlsx_rows(path):
    with zipfile.ZipFile(path) as z:
        strings=[''.join(t.itertext()) for t in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)] if 'xl/sharedStrings.xml' in z.namelist() else []
        for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('m:sheetData/m:row',NS):
            cells={}
            for c in row:
                v=c.find('m:v',NS); inline=c.find('m:is',NS)
                value=v.text if v is not None else ''.join(inline.itertext()) if inline is not None else ''
                if c.get('t')=='s' and value:value=strings[int(value)]
                cells[re.sub(r'\d','',c.get('r'))]=value or ''
            if any(cells.values()):yield int(row.get('r')),cells

def norm(v):return re.sub(r'\s+',' ',str(v or '')).strip()

def ingest(downloads=Path.home()/'Downloads'):
    DB.parent.mkdir(exist_ok=True)
    con=sqlite3.connect(DB)
    con.executescript('''DROP TABLE IF EXISTS records; DROP TABLE IF EXISTS sources;
    CREATE TABLE sources(name TEXT PRIMARY KEY,category TEXT,rows INTEGER,sha256 TEXT,export_label TEXT,imported_at TEXT);
    CREATE TABLE records(id TEXT PRIMARY KEY,entity_id TEXT,name TEXT,category TEXT,state TEXT,district TEXT,website TEXT,management TEXT,university_id TEXT,source TEXT,source_row INTEGER,original TEXT);
    CREATE INDEX entity_idx ON records(entity_id); CREATE INDEX scope_idx ON records(category,state,district);
    CREATE INDEX name_idx ON records(name COLLATE NOCASE);''')
    reports=[]
    for filename,category in FILES:
        path=downloads/filename; rows=list(xlsx_rows(path)); headers={k:norm(v).lower() for k,v in rows[2][1].items()}; count=0
        for line,cells in rows[3:]:
            original={headers[k]:v for k,v in cells.items() if k in headers}; r={k:norm(v) for k,v in original.items()}
            eid=r.get('aishe code',''); name=r.get('name',r.get('institute name',''))
            if not eid or not name:continue
            state=r.get('state',r.get('state name',''));district=r.get('district',r.get('district name',''))
            con.execute('INSERT INTO records VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(f'{category}:{line}',eid,name,category,state,district,r.get('website',''),r.get('manegement',r.get('management type','')),r.get('university aishe code',''),filename,line,json.dumps(original,ensure_ascii=False)))
            count+=1
        digest=hashlib.sha256(path.read_bytes()).hexdigest();stamp=next(iter(rows[1][1].values()))
        con.execute('INSERT INTO sources VALUES(?,?,?,?,?,?)',(filename,category,count,digest,stamp,datetime.now(timezone.utc).isoformat()))
        reports.append({'source':filename,'category':category,'records':count,'sha256':digest,'export_label':stamp})
    con.commit()
    report={'sources':reports,'raw_records':con.execute('SELECT COUNT(*) FROM records').fetchone()[0],'unique_aishe_ids':con.execute('SELECT COUNT(DISTINCT entity_id) FROM records').fetchone()[0],'states':con.execute('SELECT COUNT(DISTINCT state) FROM records').fetchone()[0],'note':'Export date is not per-record verification. Source URLs supplied separately, not invented.'}
    (DB.parent/'import-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));con.close();return report

if __name__=='__main__':print(json.dumps(ingest(),indent=2))
