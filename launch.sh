#!/bin/sh
cd "$(dirname "$0")" || exit 1
PORT=4174 exec python3 server.py
