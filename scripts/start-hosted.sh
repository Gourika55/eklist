#!/bin/sh
set -eu
python3 bootstrap_catalog.py
exec python3 server.py
