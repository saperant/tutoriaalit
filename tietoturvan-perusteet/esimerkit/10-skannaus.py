"""Salaisuuksien etsintä lähdekoodista: tunnetut muodot ja entropia."""

import math
import re
import tempfile
from collections import Counter
from pathlib import Path

# @alku saannot
SAANNOT = {
    "AWS-avain": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "yksityinen avain": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "salasana koodissa": re.compile(
        r"""(?i)(password|passwd|salasana)\s*[:=]\s*["'][^"']{4,}["']"""),
}
MERKKIJONO = re.compile(r"""["']([A-Za-z0-9+/=_-]{20,})["']""")


def entropia(s: str) -> float:
    """Shannonin entropia bitteinä merkkiä kohden."""
    n = len(s)
    return -sum(c / n * math.log2(c / n) for c in Counter(s).values())


def skannaa(juuri: Path) -> list[str]:
    loydot = []
    for polku in sorted(juuri.rglob("*.py")):
        rivit = polku.read_text().splitlines()
        for nro, rivi in enumerate(rivit, 1):
            paikka = f"{polku.relative_to(juuri)}:{nro}"
            loydot += [f"{paikka}: {nimi}"
                       for nimi, kuvio in SAANNOT.items()
                       if kuvio.search(rivi)]
            loydot += [f"{paikka}: satunnaiselta näyttävä merkkijono "
                       f"({entropia(m):.1f} bittiä/merkki)"
                       for m in MERKKIJONO.findall(rivi)
                       if entropia(m) > 4.0]
    return loydot
# @loppu saannot


with tempfile.TemporaryDirectory() as hak:
    juuri = Path(hak)
    (juuri / "asetukset.py").write_text(
        'AWS_KEY = "AKIA' + "IOSFODNN7EXAMPLE" + '"\n'
        'DB_PASSWORD = "kesa2026"\n'
        'API_TOKEN = "q8Zr2Lp0Xv7Kt4Wm9Bn3Hs6Dc1Fy5Gj"\n'
        'OTSIKKO = "Tervetuloa verkkokauppaan"\n')
    (juuri / "palvelu.py").write_text(
        "import os\nTOKEN = os.environ['API_TOKEN']\n")
    for rivi in skannaa(juuri):
        print(rivi)
