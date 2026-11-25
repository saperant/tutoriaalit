"""Kolmipistearvio (PERT) ja puskurin paikka.

Jokaiselle tehtävälle arvioidaan paras, todennäköisin ja huonoin kesto.
Verrataan PERT-kaavoja simulointiin ja kahta tapaa varautua: jokaisen
tehtävän oma varmuusvara vastaan yksi yhteinen puskuri.
"""

import math
import random

# (nimi, paras, todennäköisin, huonoin) päivinä
TEHTAVAT = [
    ("tietomalli", 2, 3, 8), ("rajapinta", 3, 5, 12),
    ("tuonti", 4, 6, 20), ("käyttöliittymä", 5, 8, 16),
    ("haku", 2, 4, 10), ("oikeudet", 3, 4, 9),
    ("raportti", 2, 3, 6), ("integraatio", 5, 10, 30),
]


# @alku pert
def pert(paras: float, todennakoisin: float, huonoin: float
         ) -> tuple[float, float]:
    """Odotusarvo ja keskihajonta PERT-kaavoilla."""
    return ((paras + 4 * todennakoisin + huonoin) / 6,
            (huonoin - paras) / 6)


odotus = sum(pert(o, m, p)[0] for _, o, m, p in TEHTAVAT)
hajonta = math.sqrt(sum(pert(o, m, p)[1] ** 2 for _, o, m, p in TEHTAVAT))
# @loppu pert


# @alku simulointi
def kesto(rng: random.Random, o: float, m: float, p: float) -> float:
    """Beeta-PERT-jakauma: vino, ja sen odotusarvo on PERT-kaavan arvo."""
    a = 1 + 4 * (m - o) / (p - o)
    b = 1 + 4 * (p - m) / (p - o)
    return o + (p - o) * rng.betavariate(a, b)


def persentiili(arvot: list[float], osuus: float) -> float:
    return sorted(arvot)[int(osuus * len(arvot))]


rng = random.Random(5)
TOISTOJA = 20_000
toteumat = [[kesto(rng, o, m, p) for _, o, m, p in TEHTAVAT]
            for _ in range(TOISTOJA)]
summat = [sum(rivi) for rivi in toteumat]
# @loppu simulointi

todennakoisimmat = sum(m for _, _, m, _ in TEHTAVAT)
print(f"todennäköisimpien summa        {todennakoisimmat:5.1f} pv")
print(f"PERT-odotusarvo                {odotus:5.1f} pv")
print(f"PERT 85 % (odotus + 1,04 s)    {odotus + 1.04 * hajonta:5.1f} pv")
print(f"simuloitu keskiarvo            {sum(summat) / TOISTOJA:5.1f} pv")
print(f"simuloitu 85 %                 {persentiili(summat, 0.85):5.1f} pv")

# @alku puskuri
omat_varat = sum(persentiili([rivi[i] for rivi in toteumat], 0.85)
                 for i in range(len(TEHTAVAT)))
yhteinen = persentiili(summat, 0.85)
print(f"jokaiselle oma 85 %:n vara     {omat_varat:5.1f} pv")
print(f"yksi yhteinen puskuri          {yhteinen:5.1f} pv "
      f"(puskuri {yhteinen - odotus:.1f} pv)")
pitaa = sum(s <= omat_varat for s in summat) / TOISTOJA
print(f"omien varojen summa pitää      {pitaa:5.1%} toistoista")
# @loppu puskuri
