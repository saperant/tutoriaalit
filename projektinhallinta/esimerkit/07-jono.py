"""Kuormitusaste ja odotusaika: miksi täysi kalenteri hidastaa.

Yksi tekijä (tai tiimi) palvelee satunnaisesti saapuvia töitä, joiden
kesto vaihtelee. Simulointia verrataan jonoteorian M/M/1-kaavaan:
keskimääräinen läpimenoaika on palveluaika / (1 - kuormitusaste).
"""

import random

TOITA = 400_000


# @alku jono
def lapimenoaika(kuormitus: float, rng: random.Random) -> float:
    """Keskimääräinen läpimenoaika palveluajan monikertoina."""
    odotus = summa = 0.0
    for _ in range(TOITA):
        palvelu = rng.expovariate(1.0)             # keskimäärin 1
        summa += odotus + palvelu
        vali = rng.expovariate(kuormitus)          # seuraava saapuu
        odotus = max(0.0, odotus + palvelu - vali)
    return summa / TOITA
# @loppu jono


rng = random.Random(8)
print("kuormitus  simuloitu  teoria  odotuksen osuus")
for kuormitus in (0.5, 0.7, 0.8, 0.9, 0.95):
    simuloitu = lapimenoaika(kuormitus, rng)
    teoria = 1 / (1 - kuormitus)
    assert abs(simuloitu - teoria) < 0.1 * teoria
    print(f"{kuormitus:8.0%}  {simuloitu:9.1f}  {teoria:6.1f}"
          f"  {1 - 1 / simuloitu:14.0%}")
