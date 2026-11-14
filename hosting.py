"""Explicit hosted-mode access control; local behavior stays unchanged."""
import hmac, os
from urllib.parse import urlsplit

def hosted():
    return os.getenv('EKLIST_HOSTED') == '1'

def authorized(headers):
    if hosted():
        secret=os.getenv('EKLIST_BACKEND_TOKEN','')
        return len(secret)>=32 and hmac.compare_digest(headers.get('Authorization',''), 'Bearer '+secret)
    host=headers.get('Host','')
    return host.split(':')[0] in ('localhost','127.0.0.1') and (not headers.get('Origin') or urlsplit(headers['Origin']).netloc==host)

def validate_hosting():
    if hosted() and len(os.getenv('EKLIST_BACKEND_TOKEN',''))<32:
        raise RuntimeError('Hosted mode requires EKLIST_BACKEND_TOKEN with at least 32 characters.')
