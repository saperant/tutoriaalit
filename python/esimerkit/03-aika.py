"""Päivämäärät ja ajat: aikavyöhykkeellinen ja naiivi aika."""

import time
from datetime import UTC, datetime, timedelta, timezone

# @alku aika
lahto = datetime(2026, 3, 28, 22, 30, tzinfo=UTC)     # vyöhyke mukana
perilla = lahto + timedelta(hours=9, minutes=45)
print(perilla.isoformat())

KESAAIKA = timezone(timedelta(hours=3), "EEST")       # kiinteä siirtymä
print(perilla.astimezone(KESAAIKA).strftime("%d.%m.%Y %H:%M %Z"))

jasennetty = datetime.fromisoformat("2026-03-29T11:15:00+03:00")
print(jasennetty == perilla)          # sama hetki eri vyöhykkeissä

naiivi = datetime(2026, 3, 29, 8, 15)                 # ei vyöhykettä
try:
    print(naiivi < perilla)
except TypeError as virhe:
    print("TypeError:", virhe)

alku = time.monotonic()               # kestot kellosta, joka ei hyppää
kesto_s = time.monotonic() - alku
print(kesto_s >= 0)
# @loppu aika
