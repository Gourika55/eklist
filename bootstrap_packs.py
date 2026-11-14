"""Restore the bundled public evidence library without overwriting live refreshes."""
import json
from pathlib import Path
import packs

def restore(path=None):
    path=Path(path or packs.BASE/'config'/'opportunity-seed.json')
    data=json.loads(path.read_text());added=0
    with packs.connect() as c:
        for source in data['sources']:
            # A live source wins over the bundled historical snapshot.
            if c.execute('SELECT 1 FROM pack_sources WHERE id=?',(source['id'],)).fetchone():continue
            c.execute('INSERT INTO pack_sources VALUES(?,?,?,?,?,?)',(source['id'],source['category'],source['url'],source['title'],source['status'],json.dumps(source)))
            for record in data['records']:
                if record['source_id']==source['id']:
                    c.execute('INSERT INTO pack_records VALUES(?,?,?,?,?)',(record['id'],record['source_id'],record['name'],record['kind'],record['payload']));added+=1
    return added
if __name__=='__main__':print(f'Public evidence library restored: {restore()} records added',flush=True)
