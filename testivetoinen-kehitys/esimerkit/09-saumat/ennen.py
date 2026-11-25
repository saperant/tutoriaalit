"""Tilausvahvistus: kello, arpa ja tulostus kietoutuvat logiikkaan."""

import random
from datetime import datetime, timedelta

MERKIT = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


# @alku ennen
def vahvista_tilaus(tilausnumero: int) -> None:
    nyt = datetime.now()
    lahto = nyt.date()
    if nyt.hour >= 15:              # iltapäivän tilaus lähtee huomenna
        lahto += timedelta(days=1)
    while lahto.weekday() >= 5:     # viikonloppuna ei lähetetä
        lahto += timedelta(days=1)
    saapuu = lahto + timedelta(days=2)
    while saapuu.weekday() >= 5:
        saapuu += timedelta(days=1)
    koodi = "".join(random.choice(MERKIT) for _ in range(6))
    print(f"Tilaus {tilausnumero} lähtee {lahto:%d.%m.} ja saapuu "
          f"{saapuu:%d.%m.} Seurantakoodi: {koodi}")
# @loppu ennen
