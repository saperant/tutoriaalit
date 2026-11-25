"""Usean tiimin ominaisuus valmistuu, kun viimeinenkin tiimi on valmis."""

import random

SIEMEN = 11
TOISTOJA = 20_000


# @alku todennakoisyys
def ajallaan(tiimeja: int, p: float) -> float:
    """Kaikki tiimit ajallaan, kun kukin onnistuu toisista riippumatta
    todennäköisyydellä p."""
    return p ** tiimeja
# @loppu todennakoisyys


def simuloitu(tiimeja: int, p: float, rng: random.Random) -> float:
    osumat = sum(all(rng.random() < p for _ in range(tiimeja))
                 for _ in range(TOISTOJA))
    return osumat / TOISTOJA


rng = random.Random(SIEMEN)
print("tiimejä   p = 0,9   p = 0,8   p = 0,7")
for tiimeja in range(1, 7):
    arvot = [ajallaan(tiimeja, p) for p in (0.9, 0.8, 0.7)]
    assert abs(simuloitu(tiimeja, 0.8, rng) - arvot[1]) < 0.01
    print(f"{tiimeja:>7}" + "".join(f"{a:>10.0%}" for a in arvot))
