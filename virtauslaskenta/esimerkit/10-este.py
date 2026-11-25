"""Virtaus neliöesteen ohi: pyörrerata ja Strouhalin luku.

Reynoldsin luvulla 100 esteen taakse ei jää pysyvää pyörreparia, vaan
pyörteet irtoavat vuorotellen ylä- ja alareunasta. Irtoamisen taajuus
mitataan esteen takaa pystynopeuden vaihtelusta."""

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "07-virta"))
from virta import (  # noqa: E402
    Ratkaisija,
    Reuna,
    Taulukko,
    Tehtava,
    Tila,
    vakaa_askel,
)

# @alku tehtava
SIVU = 0.2            # esteen sivu d; kanavan korkeus on 1
PITUUS = 4.0
ESTE_X = 1.0          # esteen keskikohta
REYNOLDS = 100.0      # U d / nu, U = sisäänvirtauksen nopeus 1
LOPPU = 24.0


def tehtava(ny: int, vastavirta: float) -> tuple[Tehtava, tuple[int, int]]:
    """Palauttaa tehtävän ja mittapisteen (v:n indeksit) esteen takana."""
    h = 1.0 / ny
    k = round(SIVU / h)
    i0 = round(ESTE_X / h) - k // 2
    # Este on yhden ruudun verran keskilinjan yläpuolella: täysin
    # symmetrisessä tehtävässä irtoaminen käynnistyisi vasta
    # pyöristysvirheistä.
    j0 = ny // 2 - k // 2 + 1
    este = np.zeros((round(PITUUS * ny), ny), dtype=np.bool_)
    este[i0:i0 + k, j0:j0 + k] = True
    teht = Tehtava(este.shape[0], ny, PITUUS, 1.0, SIVU / REYNOLDS,
                   vasen=Reuna("sisään", 1.0), oikea=Reuna("ulos"),
                   este=este, vastavirta=vastavirta)
    return teht, (i0 + 2 * k, ny // 2)
# @loppu tehtava


# @alku ajo
@dataclass
class Ajo:
    teht: Tehtava
    tila: Tila
    ajat: Taulukko
    v_mitta: Taulukko         # pystynopeus mittapisteessä


def aja(ny: int, vastavirta: float = 0.0, loppu: float = LOPPU) -> Ajo:
    teht, (im, jm) = tehtava(ny, vastavirta)
    ratkaisija = Ratkaisija(teht)
    tila = ratkaisija.lepotila()
    dt = vakaa_askel(teht, 2.2)
    askelia = round(loppu / dt)
    ajat = np.zeros(askelia)
    arvot = np.zeros(askelia)
    for n in range(askelia):
        tila = ratkaisija.askel(tila, dt)
        ajat[n], arvot[n] = tila.t, tila.v[im, jm]
    return Ajo(teht, tila, ajat, arvot)


def jakso_ja_vaihtelu(ajo: Ajo, alku: float = 0.6 * LOPPU
                      ) -> tuple[float, float]:
    """Värähtelyn jakso nousevista nollanylityksistä ja huipusta
    huippuun -vaihtelu ajan alku jälkeen."""
    valinta = ajo.ajat > alku
    t = ajo.ajat[valinta]
    s = ajo.v_mitta[valinta] - float(np.mean(ajo.v_mitta[valinta]))
    k = np.flatnonzero((s[:-1] < 0.0) & (s[1:] >= 0.0))
    ylitykset = t[k] - s[k] * (t[k + 1] - t[k]) / (s[k + 1] - s[k])
    return (float(np.mean(np.diff(ylitykset))),
            float(np.max(s) - np.min(s)))
# @loppu ajo


# @alku taulukko
if __name__ == "__main__":
    print("ruutuja/sivu d  advektio       jakso  Strouhal  v:n vaihtelu")
    for ny, nimi, vastavirta in ((30, "keskeis", 0.0),
                                 (30, "sekoitus 0,3", 0.3),
                                 (30, "vastavirta", 1.0),
                                 (40, "keskeis", 0.0)):
        ajo = aja(ny, vastavirta)
        jakso, vaihtelu = jakso_ja_vaihtelu(ajo)
        print(f"{round(SIVU * ny):14d}  {nimi:12s} {jakso:7.3f}"
              f" {SIVU / jakso:9.3f} {vaihtelu:13.2f}")
# @loppu taulukko
