"""Kymmenen tehtävän projekti: todennäköisimpien kestojen summa ei ole
todennäköinen kokonaiskesto.

Jokaisen tehtävän kesto on vino: nopeimmillaan 3, todennäköisimmin 5 ja
hitaimmillaan 15 päivää (kolmiojakauma).
"""

import random

TEHTAVIA = 10
PARAS, TODENNAKOISIN, HUONOIN = 3.0, 5.0, 15.0
TOISTOJA = 20_000


# @alku simulointi
def projektin_kesto(rng: random.Random) -> float:
    """Yksi mahdollinen toteuma: tehtävien kestojen summa."""
    return sum(rng.triangular(PARAS, HUONOIN, TODENNAKOISIN)
               for _ in range(TEHTAVIA))


rng = random.Random(2026)
kestot = sorted(projektin_kesto(rng) for _ in range(TOISTOJA))
# @loppu simulointi


def persentiili(jarjestetty: list[float], p: float) -> float:
    return jarjestetty[min(len(jarjestetty) - 1, int(p * len(jarjestetty)))]


# @alku tulos
suunnitelma = TEHTAVIA * TODENNAKOISIN
onnistui = sum(k <= suunnitelma for k in kestot) / TOISTOJA
print(f"todennäköisimpien summa   {suunnitelma:5.0f} pv")
print(f"odotusarvo                {sum(kestot) / TOISTOJA:5.0f} pv")
for p in (0.50, 0.85, 0.95):
    print(f"{p:4.0%}:n varmuus           {persentiili(kestot, p):5.0f} pv")
print(f"suunnitelma {suunnitelma:.0f} pv pitää   {onnistui:5.1%} toistoista")
# @loppu tulos
