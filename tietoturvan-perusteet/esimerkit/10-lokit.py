"""Tunnistetietojen vuodot lokeihin ja niiden peittäminen."""

import logging
import re
import sys

# @alku suodatin
PEITETTAVAT = [
    (re.compile(r"(?i)(authorization:\s*bearer\s+)\S+"), r"\1[PEITETTY]"),
    (re.compile(r"(?i)\b(password|salasana|token)=[^&\s]+"),
     r"\1=[PEITETTY]"),
    (re.compile(r"\b(\d{4})\d{8,11}(\d{4})\b"), r"\1********\2"),
]


class Peittaja(logging.Filter):
    """Viimeinen puolustuslinja: salaisuuksia ei pitäisi lokittaa lainkaan,
    mutta suodatin estää vahingot, joita koodikatselmointi ei huomaa."""

    def filter(self, tietue: logging.LogRecord) -> bool:
        viesti = tietue.getMessage()
        for kuvio, korvaus in PEITETTAVAT:
            viesti = kuvio.sub(korvaus, viesti)
        tietue.msg, tietue.args = viesti, None
        return True
# @loppu suodatin


kasittelija = logging.StreamHandler(sys.stdout)
kasittelija.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
loki = logging.getLogger("kauppa")
loki.addHandler(kasittelija)
loki.setLevel(logging.INFO)

pyynto = "POST /kirjaudu?kayttaja=aino&salasana=kesa2026"
otsake = "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.e30.abc"
loki.info("ilman suodatinta: %s", pyynto)
kasittelija.addFilter(Peittaja())
loki.info("pyyntö: %s", pyynto)
loki.info("otsake: %s", otsake)
loki.info("maksu kortilla %s hylättiin", "4111111111111111")
