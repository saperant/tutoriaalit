"""Reunan paikan ja muodon vaikutus tulokseen.

Neliöeste kanavassa, Reynoldsin luku esteen sivun mukaan 20. Esteen
taakse syntyy pyörrepari; sen pituus on tulos, jota seurataan, kun
sisään- ja ulosvirtausreunaa siirretään."""

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "07-virta"))
from virta import (  # noqa: E402
    Ratkaisija,
    Reuna,
    Taulukko,
    Tehtava,
    tasapainoon,
    vakaa_askel,
)

# @alku tehtava
NY = 24
H = 1.0 / NY
SIVU = 0.25           # esteen sivu; kanavan korkeus on 1
REYNOLDS = 20.0


def pyorteen_pituus(etumatka: float, jalkimatka: float,
                    profiili: str = "tasainen") -> float:
    """Takaisinvirtausalueen pituus esteen sivuina. etumatka on
    sisäänvirtausreunan etäisyys esteen etureunasta ja jalkimatka
    ulosvirtausreunan etäisyys takareunasta. Palauttaa nan, jos
    takaisinvirtaus ulottuu ulosvirtausreunalle asti."""
    nx = round((etumatka + SIVU + jalkimatka) / H)
    i0, k = round(etumatka / H), round(SIVU / H)
    este = np.zeros((nx, NY), dtype=np.bool_)
    este[i0:i0 + k, NY // 2 - k // 2:NY // 2 + k // 2] = True
    y: Taulukko = (np.arange(NY, dtype=np.float64) + 0.5) * H
    sisaan = 6.0 * y * (1.0 - y) if profiili == "paraabeli" else np.ones(NY)
    teht = Tehtava(nx, NY, nx * H, 1.0, SIVU / REYNOLDS,
                   vasen=Reuna("sisään", sisaan), oikea=Reuna("ulos"),
                   este=este)
    ratkaisija = Ratkaisija(teht)
    tila, _ = tasapainoon(ratkaisija, ratkaisija.lepotila(),
                          vakaa_askel(teht, 2.5))
    # Keskilinjan nopeus esteen takana: etsitään merkin vaihtuminen.
    uc = 0.5 * (tila.u[i0 + k:, NY // 2 - 1] + tila.u[i0 + k:, NY // 2])
    myota = np.flatnonzero(uc[1:] > 0.0)
    if myota.size == 0 or float(np.min(tila.u[-1, :])) < 0.0:
        return math.nan
    m = int(myota[0]) + 1
    nolla = (m - 1) + uc[m - 1] / (uc[m - 1] - uc[m])
    return float(nolla * H / SIVU)
# @loppu tehtava


# @alku taulukko
def rivi(nimi: str, pituus: float, viite: float) -> None:
    if math.isnan(pituus):
        print(f"  {nimi:34s} takaisinvirtaus ulosvirtausreunalla")
    else:
        ero = round(100.0 * (pituus / viite - 1.0), 1) + 0.0
        print(f"  {nimi:34s} {pituus:6.3f} {ero:+7.1f} %")


viite = pyorteen_pituus(3.0, 3.0)
print(f"viite: reunat kolmen yksikön päässä, pyörteen pituus {viite:.3f}"
      " sivua")
print("sisäänvirtausreunan etäisyys esteestä (ulosvirtaus 3,0)")
for etumatka in (0.5, 1.0):
    rivi(f"tasainen profiili, {etumatka:.1f}",
         pyorteen_pituus(etumatka, 3.0), viite)
rivi("paraabeli, 1.0", pyorteen_pituus(1.0, 3.0, "paraabeli"), viite)
print("ulosvirtausreunan etäisyys esteestä (sisäänvirtaus 3,0)")
for jalkimatka in (0.25, 0.375, 0.75, 1.5):
    rivi(f"{jalkimatka:.3f}", pyorteen_pituus(3.0, jalkimatka), viite)
# @loppu taulukko
