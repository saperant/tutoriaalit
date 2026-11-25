"""Milloin laskenta on valmis: jäännös ja seurattava suure.

Onkalovirtaus (Re = 100, hila 32 x 32) marssitetaan kohti tasapainoa.
Jäännös on nopeuden suurin muutosnopeus; seurattava suure on
pääpyörteen voimakkuus."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "07-virta"))
from virta import (  # noqa: E402
    Ratkaisija,
    Reuna,
    Tehtava,
    vakaa_askel,
    virtafunktio,
)

# @alku seuranta
teht = Tehtava(32, 32, 1.0, 1.0, 0.01, yla=Reuna("seinä", 1.0))
ratkaisija = Ratkaisija(teht)
dt = vakaa_askel(teht, 1.0, "Euler")
tila = ratkaisija.lepotila()
historia: list[tuple[int, float, float]] = []     # askel, jäännös, psi_min
for askel in range(1, 2401):
    uusi = ratkaisija.askel(tila, dt, "Euler")
    jaannos = float(np.max(np.abs(uusi.u - tila.u))) / dt
    tila = uusi
    if askel % 200 == 0:
        psi = float(np.min(virtafunktio(teht, tila.u)))
        historia.append((askel, jaannos, psi))
# @loppu seuranta

# @alku taulukko
lopullinen = historia[-1][2]
print("askel   aika   jäännös   pyörteen voimakkuus  ero lopulliseen")
for askel, jaannos, psi in historia:
    ero = round(100.0 * (psi / lopullinen - 1.0), 2) + 0.0
    print(f"{askel:5d} {askel * dt:6.1f} {jaannos:9.1e} {psi:14.5f}"
          f" {ero:15.2f} %")
# @loppu taulukko
