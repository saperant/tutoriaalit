"""Luonnolliset reunaehdot: lämmitetty ja ilmalla jäähdytetty levy.

Alumiinilevy 100 mm x 50 mm (paksuus 2 mm): vasemmalta reunalta tulee
lämpövuo, oikea reuna jäähtyy ilmaan, ylä- ja alareuna on eristetty."""

import sys
from pathlib import Path

import numpy as np
import numpy.typing as npt
from scipy.sparse.linalg import spsolve

sys.path.insert(0, str(Path(__file__).resolve().parent / "07-pienfem"))
from pienfem import (  # noqa: E402
    Indeksit,
    Taulukko,
    Verkko,
    jaykkyys,
    reunakuorma,
    reunamatriisi,
    suorakulmio,
)

K = 200.0                  # W/(m K)
H = 50.0                   # W/(m² K)
T_ILMA = 20.0
VUO = 5000.0               # W/m² lämmittimestä
LEVEYS, KORKEUS = 0.100, 0.050


# @alku ratkaisu
def ratkaise_levy(verkko: Verkko, lammitin: Indeksit,
                  jaahdytys: Indeksit) -> Taulukko:
    """(K + H_reuna) T = vuo + H_reuna T_ilma. Eristetty reuna ei vaadi
    mitään: se on heikon muodon oletus."""
    hm = reunamatriisi(verkko, jaahdytys, H)
    a = jaykkyys(verkko, K) + hm
    b = reunakuorma(verkko, lammitin, VUO) + hm @ np.full(
        len(verkko.pisteet), T_ILMA)
    t: Taulukko = spsolve(a.tocsc(), b)
    return t
# @loppu ratkaisu


def sarmat_kun(verkko: Verkko, ehto: npt.NDArray[np.bool_]) -> Indeksit:
    """Reunasärmät, joiden molemmat päät toteuttavat ehdon."""
    sarmat = verkko.reunasarmat()
    valitut: Indeksit = sarmat[ehto[sarmat[:, 0]] & ehto[sarmat[:, 1]]]
    return valitut


# @alku koe
verkko = suorakulmio(40, 20, LEVEYS, KORKEUS)
x, y = verkko.pisteet[:, 0], verkko.pisteet[:, 1]
oikea = sarmat_kun(verkko, x > LEVEYS - 1e-9)

# 1. Koko vasen reuna lämmittää: tehtävä on yksiulotteinen.
vasen = sarmat_kun(verkko, x < 1e-9)
t = ratkaise_levy(verkko, vasen, oikea)
print(f"koko reuna: vasen {t[x < 1e-9].max():.3f} °C "
      f"(tarkka {T_ILMA + VUO / H + VUO * LEVEYS / K:.3f}), "
      f"oikea {t[x > LEVEYS - 1e-9].max():.3f} °C "
      f"(tarkka {T_ILMA + VUO / H:.3f})")

# 2. Lämmitin vain reunan keskikolmanneksella.
osa = sarmat_kun(verkko, (x < 1e-9) & (y > KORKEUS / 3 - 1e-9)
                 & (y < 2 * KORKEUS / 3 + 1e-9))
t = ratkaise_levy(verkko, osa, oikea)
teho_sisaan = VUO * float(np.sum(np.linalg.norm(
    verkko.pisteet[osa[:, 1]] - verkko.pisteet[osa[:, 0]], axis=1)))
hm = reunamatriisi(verkko, oikea, H)
teho_ulos = float(np.sum(hm @ (t - T_ILMA)))
print(f"osalämmitin: sisään {teho_sisaan:.3f} W/m, ulos {teho_ulos:.3f} W/m")
print(f"  kuumin kohta {t.max():.2f} °C, kylmin {t.min():.2f} °C")
# @loppu koe
