"""Restore only the institution catalogue on ephemeral hosts; verify before replacing."""
import gzip,hashlib,os,sqlite3,tempfile,urllib.request
from pathlib import Path
BASE=Path(__file__).resolve().parent

def install_archive(archive,destination,expected):
    if len(expected)!=64 or hashlib.sha256(Path(archive).read_bytes()).hexdigest()!=expected.lower():
        raise ValueError('Catalogue archive SHA-256 mismatch')
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent,delete=False,suffix='.sqlite') as f:
        temporary=Path(f.name)
        try:
            with gzip.open(archive,'rb') as src:
                count=0
                while chunk:=src.read(1024*1024):
                    count+=len(chunk)
                    if count>250*1024*1024:raise ValueError('Expanded catalogue exceeds 250 MB')
                    f.write(chunk)
            f.flush()
            with sqlite3.connect(f'file:{temporary}?mode=ro',uri=True) as db:
                if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Invalid catalogue')
                count=db.execute('SELECT count(*) FROM records').fetchone()[0]
                db.execute('SELECT name,category,rows,sha256,export_label,imported_at FROM sources LIMIT 1')
                if count==0:raise ValueError('Empty catalogue seed')
            temporary.replace(destination)
            return count
        finally:
            temporary.unlink(missing_ok=True)

def main():
    destination=BASE/'data'/'eklist.sqlite'
    if destination.exists():
        with sqlite3.connect(f'file:{destination}?mode=ro',uri=True) as db:
            try:
                if db.execute('SELECT count(*) FROM records').fetchone()[0]>0:
                    print('Existing catalogue retained',flush=True);return
            except sqlite3.OperationalError:pass
    url=os.getenv('EKLIST_CATALOG_SEED_URL','')
    if not url.startswith('https://'):raise RuntimeError('Set EKLIST_CATALOG_SEED_URL to an HTTPS .sqlite.gz download URL')
    with tempfile.NamedTemporaryFile(suffix='.gz') as tmp:
        with urllib.request.urlopen(url,timeout=120) as response:
            if not response.geturl().startswith('https://'):raise RuntimeError('Seed redirect must use HTTPS')
            count=0
            while chunk:=response.read(1024*1024):
                count+=len(chunk)
                if count>100*1024*1024:raise ValueError('Compressed catalogue exceeds 100 MB')
                tmp.write(chunk)
        tmp.flush()
        rows=install_archive(tmp.name,destination,os.getenv('EKLIST_CATALOG_SEED_SHA256',''))
        print(f'Catalogue restored: {rows} source rows',flush=True)
if __name__=='__main__':main()
