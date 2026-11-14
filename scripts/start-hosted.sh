#!/bin/sh
set -eu
python3 bootstrap_catalog.py
python3 bootstrap_packs.py
exec python3 server.py
