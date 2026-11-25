"""L-alue: sisäänpäin kääntyvä kulma hidastaa suppenemista.

Ratkaisu u = r^(2/3) sin(2 theta / 3) toteuttaa Laplacen yhtälön, mutta
sen gradientti kasvaa rajatta kulmassa. Reuna-arvot otetaan tarkasta
ratkaisusta, joten virhe voidaan laskea."""

import math
import sys
from pathlib import Path

import numpy as np

# Luvun 7 kirjasto on viereisessä hakemistossa.
sys.path.insert(0, str(Path(__file__).resolve().parent / "07-pienfem"))
from pienfem import (  # noqa: E402
    Taulukko,
    jaykkyys,
    l2_virhe,
    l_alue,
    ratkaise,
)


# @alku tarkka
def tarkka(x: Taulukko, y: Taulukko) -> Taulukko:
    r = np.hypot(x, y)
    theta = np.mod(np.arctan2(y, x), 2.0 * math.pi)     # 0 … 3 pi / 2
    tulos: Taulukko = r ** (2.0 / 3.0) * np.sin(2.0 * theta / 3.0)
    return tulos
# @loppu tarkka


# @alku koe
print("ruutuja/sivu  solmuja   L2-virhe  kertaluku  virhe kulman vieressä")
edellinen = 0.0
for n in (4, 8, 16, 32, 64):
    verkko = l_alue(n)
    reuna = verkko.reunasolmut()
    x, y = verkko.pisteet[:, 0], verkko.pisteet[:, 1]
    u = ratkaise(jaykkyys(verkko), np.zeros(len(x)), reuna,
                 tarkka(x[reuna], y[reuna]))
    virhe = l2_virhe(verkko, u, tarkka)
    # Kulmaa lähin sisäsolmu on etäisyydellä h lävistäjällä.
    lahin = int(np.argmin(np.hypot(x + 1.0 / n, y - 1.0 / n)))
    paikallinen = abs(u[lahin] - float(tarkka(x[lahin:lahin + 1],
                                              y[lahin:lahin + 1])[0]))
    p = f"{math.log2(edellinen / virhe):9.2f}" if edellinen else "        -"
    print(f"{n:12d} {len(x):8d} {virhe:10.2e} {p} {paikallinen:14.2e}")
    edellinen = virhe
# @loppu koe
