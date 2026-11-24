"""Pikaoppaan turvalliset perusmuodot Pythonilla."""

import hashlib
import hmac
import os
import secrets
import sqlite3
import subprocess
import tempfile
from pathlib import Path

# @alku satunnaisuus
istunto = secrets.token_urlsafe(32)          # ei random-modulia
koodi = f"{secrets.randbelow(10**6):06d}"     # kertakäyttökoodi
# @loppu satunnaisuus

# @alku vertailu
avain = secrets.token_bytes(32)
tunniste = hmac.new(avain, b"viesti", hashlib.sha256).hexdigest()
aito = hmac.compare_digest(tunniste, tunniste)   # vakioaikainen
# @loppu vertailu

# @alku salasana
suola = secrets.token_bytes(16)
tiiviste = hashlib.scrypt(b"salasana", salt=suola, n=2**14, r=8, p=1)
# @loppu salasana

# @alku sql
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE t (nimi TEXT)")
nimi = "x' OR '1'='1"
rivit = db.execute("SELECT * FROM t WHERE nimi = ?", (nimi,)).fetchall()
# @loppu sql

# @alku komento
tulos = subprocess.run(["echo", nimi],  # noqa: S603, S607
                       capture_output=True, text=True, check=True)
# @loppu komento

with tempfile.TemporaryDirectory() as hak:
    juuri = Path(hak)
    # @alku polku
    polku = (juuri / "raportti.txt").resolve()
    if not polku.is_relative_to(juuri.resolve()):
        raise PermissionError(polku)
    fd = os.open(polku, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                 | os.O_NOFOLLOW, 0o600)
    os.close(fd)
    # @loppu polku

print(len(istunto), len(koodi), aito, len(tiiviste), rivit,
      tulos.stdout.strip())
