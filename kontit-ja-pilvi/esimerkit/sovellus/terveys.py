"""Kontin terveystarkistus: onnistuu, jos palvelu vastaa /terveys."""

import os
import sys
import urllib.request

osoite = f"http://127.0.0.1:{os.environ.get('PORTTI', '8080')}/terveys"
try:
    urllib.request.urlopen(osoite, timeout=2)
except OSError:
    sys.exit(1)
