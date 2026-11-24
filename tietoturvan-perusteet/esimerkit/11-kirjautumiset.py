"""Hyökkäysten tunnistus kirjautumislokista."""

import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

IKKUNA = timedelta(minutes=10)


@dataclass(frozen=True)
class Tapahtuma:
    aika: datetime
    onnistui: bool
    kayttaja: str
    ip: str


def jasenna(rivi: str) -> Tapahtuma:
    aika, tulos, kayttaja, ip = rivi.split()
    return Tapahtuma(datetime.fromisoformat(aika), tulos == "onnistui",
                     kayttaja.removeprefix("kayttaja="),
                     ip.removeprefix("ip="))


# @alku tunnistus
def tunnista(tapahtumat: list[Tapahtuma]) -> list[str]:
    halytykset = []
    virheet: dict[str, list[datetime]] = defaultdict(list)
    kohteet: dict[str, dict[str, datetime]] = defaultdict(dict)
    for t in tapahtumat:
        tuoreet = [a for a in virheet[t.kayttaja] if t.aika - a <= IKKUNA]
        if t.onnistui:
            if len(tuoreet) >= 3:
                halytykset.append(
                    f"{t.aika:%H:%M} KRIITTINEN onnistunut kirjautuminen "
                    f"{len(tuoreet)} virheen jälkeen: {t.kayttaja} ({t.ip})")
            virheet[t.kayttaja].clear()
            continue
        virheet[t.kayttaja] = [*tuoreet, t.aika]
        if len(virheet[t.kayttaja]) == 5:
            halytykset.append(f"{t.aika:%H:%M} arvaushyökkäys: "
                              f"{t.kayttaja} ({t.ip})")
        tilit = {k: a for k, a in kohteet[t.ip].items()
                 if t.aika - a <= IKKUNA}
        tilit[t.kayttaja] = t.aika
        kohteet[t.ip] = tilit
        if len(tilit) == 4:
            halytykset.append(f"{t.aika:%H:%M} salasanaruiskutus "
                              f"osoitteesta {t.ip}: {len(tilit)} tiliä")
    return halytykset
# @loppu tunnistus


tapahtumat = [jasenna(rivi) for rivi in sys.stdin if rivi.strip()]
for halytys in tunnista(tapahtumat):
    print(halytys)
