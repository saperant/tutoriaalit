"""Verkon laatu: suuri kulma on vaarallinen, pieni kulma ei.

Sama Poissonin tehtävä (ratkaisu sin(pi x) sin(pi y)) verkoilla, joiden
kolmiot ovat litteitä kahdella eri tavalla: suorakulmaisina ja niin,
että yksi kulma lähestyy 180 astetta."""

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "07-pienfem"))
from pienfem import (  # noqa: E402
    Taulukko,
    Verkko,
    elementti,
    jaykkyys,
    kuorma,
    l2_virhe,
    ratkaise,
    suorakulmio,
)


# @alku verkot
def siirretty(nx: int, ny: int) -> Verkko:
    """Sama solmumäärä kuin suorakulmiolla, mutta joka toista solmuriviä
    on siirretty puoli ruutua sivulle: litteisiin kolmioihin syntyy
    lähes 180 asteen kulma."""
    verkko = suorakulmio(nx, ny)
    pisteet = verkko.pisteet.copy()
    rivi = np.rint(pisteet[:, 1] * ny).astype(int)
    sisalla = (pisteet[:, 0] > 1e-9) & (pisteet[:, 0] < 1.0 - 1e-9)
    pisteet[sisalla & (rivi % 2 == 1), 0] += 0.5 / nx
    return Verkko(pisteet, verkko.kolmiot)


def kulmat(verkko: Verkko) -> tuple[float, float]:
    """Verkon pienin ja suurin kulma asteina."""
    pienin, suurin = 180.0, 0.0
    for solmut in verkko.kolmiot:
        p = verkko.pisteet[solmut]
        for i in range(3):
            a, b = p[i - 1] - p[i], p[(i + 1) % 3] - p[i]
            kulma = math.degrees(math.acos(
                float(a @ b) / float(np.linalg.norm(a) * np.linalg.norm(b))))
            pienin, suurin = min(pienin, kulma), max(suurin, kulma)
    return pienin, suurin
# @loppu verkot


# @alku virhe
def tarkka(x: Taulukko, y: Taulukko) -> Taulukko:
    return np.sin(math.pi * x) * np.sin(math.pi * y)


def energiavirhe(verkko: Verkko, u: Taulukko) -> float:
    """Gradientin virhe L2-normissa, kvadratuuri kolmion painopisteessä."""
    summa = 0.0
    for solmut in verkko.kolmiot:
        p = verkko.pisteet[solmut]
        g, ala = elementti(p)
        x, y = p.mean(axis=0)
        tarkka_g = math.pi * np.array(
            [math.cos(math.pi * x) * math.sin(math.pi * y),
             math.sin(math.pi * x) * math.cos(math.pi * y)])
        summa += ala * float(np.sum((u[solmut] @ g - tarkka_g) ** 2))
    return math.sqrt(summa)


print("verkko               solmuja  pienin  suurin  energiavirhe  L2-virhe")
for nimi, verkko in (("8 x 8", suorakulmio(8, 8)),
                     ("8 x 64 suora", suorakulmio(8, 64)),
                     ("8 x 64 siirretty", siirretty(8, 64)),
                     ("8 x 256 suora", suorakulmio(8, 256)),
                     ("8 x 256 siirretty", siirretty(8, 256))):
    reuna = verkko.reunasolmut()
    u = ratkaise(jaykkyys(verkko), kuorma(
        verkko, lambda x, y: 2.0 * math.pi**2 * tarkka(x, y)),
        reuna, np.zeros(len(reuna)))
    pienin, suurin = kulmat(verkko)
    print(f"{nimi:20s} {len(u):7d} {pienin:7.1f} {suurin:7.1f} "
          f"{energiavirhe(verkko, u):13.3f} "
          f"{l2_virhe(verkko, u, tarkka):9.4f}")
# @loppu virhe
