"""Käskevä skripti ja deklaratiivinen kuvaus samasta ympäristöstä.

Skripti kertoo askeleet, kuvaus lopputuloksen. Ero näkyy, kun sama
ajetaan toisen kerran tai kun joku on muuttanut ympäristöä käsin.
"""

import json
from pathlib import Path

from toimitus.tasmaytys import Tila, suunnittele, toteuta, tulosta

HALUTTU: Tila = json.loads(
    Path(__file__).with_name("haluttu.json").read_text("utf-8"))


# @alku kaskeva
def asenna_kaskevasti(palvelimet: list[str]) -> None:
    """Askelet: 'lisää kolme verkkopalvelinta'. Toinen ajo lisää toiset."""
    for _ in range(3):
        palvelimet.append(f"verkkopalvelu-{len(palvelimet) + 1}")
# @loppu kaskeva


palvelimet: list[str] = []
asenna_kaskevasti(palvelimet)
asenna_kaskevasti(palvelimet)
print(f"käskevä skripti kahdesti: {len(palvelimet)} palvelinta")

# @alku deklaratiivinen
ymparisto: Tila = {"verkkopalvelu": {"kopioita": 1, "versio": "1.3.2"},
                   "vanha-raportointi": {"kopioita": 1}}
print("suunnitelma:")
tulosta(suunnittele(HALUTTU, ymparisto))
toteuta(HALUTTU, ymparisto)
print("suunnitelma toteutuksen jälkeen:")
tulosta(suunnittele(HALUTTU, ymparisto))
# @loppu deklaratiivinen

# Joku korjaa hälytystä käsin ja unohtaa kertoa: ympäristö ajautuu.
ymparisto["verkkopalvelu"]["kopioita"] = 6
ymparisto["kuormantasaaja"]["portti"] = 8443
print("ajautuma käsin tehdyn muutoksen jälkeen:")
tulosta(suunnittele(HALUTTU, ymparisto))
