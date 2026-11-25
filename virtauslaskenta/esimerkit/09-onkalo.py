"""Kansivetoinen onkalo: neliö, jonka kansi liikkuu.

Vakiotehtävä, jolla kokoonpuristumattoman virtauksen ohjelmat
tarkistetaan. Tarkkaa ratkaisua ei ole, joten tulos tarkistetaan
kolmella hilalla ja Richardsonin ekstrapoloinnilla."""

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "07-virta"))
from virta import (  # noqa: E402
    Ratkaisija,
    Reuna,
    Tehtava,
    Tila,
    tasapainoon,
    vakaa_askel,
    virtafunktio,
)


# @alku onkalo
def onkalo(reynolds: float, n: int, kaavio: str = "Euler"
           ) -> tuple[Tehtava, Tila, int]:
    """Yksikköneliö, kannen nopeus 1, joten nu = 1 / Re."""
    teht = Tehtava(n, n, 1.0, 1.0, 1.0 / reynolds, yla=Reuna("seinä", 1.0))
    ratkaisija = Ratkaisija(teht)
    tila, askelia = tasapainoon(ratkaisija, ratkaisija.lepotila(),
                                vakaa_askel(teht, 1.0, kaavio), kaavio=kaavio)
    return teht, tila, askelia


@dataclass(frozen=True)
class Tunnusluvut:
    psi: float                    # pääpyörteen voimakkuus (psin minimi)
    keskus: tuple[float, float]   # pääpyörteen keskipiste
    u_min: float                  # pienin u pystysuoralla keskilinjalla
    v_max: float                  # suurin v vaakasuoralla keskilinjalla
    v_min: float


def tunnusluvut(teht: Tehtava, tila: Tila) -> Tunnusluvut:
    psi = virtafunktio(teht, tila.u)
    i, j = np.unravel_index(int(np.argmin(psi)), psi.shape)
    n = teht.nx
    return Tunnusluvut(float(psi[i, j]), (int(i) / n, int(j) / n),
                       float(np.min(tila.u[n // 2, :])),
                       float(np.max(tila.v[:, n // 2])),
                       float(np.min(tila.v[:, n // 2])))
# @loppu onkalo


# @alku hilat
def richardson(a: float, b: float, c: float) -> tuple[float, float, float]:
    """Kolme tulosta hiloilla h, h/2 ja h/4: havaittu kertaluku,
    ekstrapoloitu arvo ja tiheimmän hilan virhearvio (GCI)."""
    p = math.log2((b - a) / (c - b))
    raja = c + (c - b) / (2.0**p - 1.0)
    gci = 1.25 * abs(c - b) / (2.0**p - 1.0)
    return p, raja, gci


if __name__ == "__main__":
    print("Re = 100")
    print("  hila  askelia   psi_min   keskus          u_min    v_max"
          "    v_min")
    tulokset = []
    for n in (16, 32, 64):
        teht, tila, askelia = onkalo(100.0, n)
        t = tunnusluvut(teht, tila)
        tulokset.append(t)
        print(f"  {n:4d} {round(askelia, -2):8d} {t.psi:9.5f}"
              f"   ({t.keskus[0]:.3f}, {t.keskus[1]:.3f})"
              f" {t.u_min:8.4f} {t.v_max:8.4f} {t.v_min:8.4f}")
    print("  suure    kertaluku  ekstrapoloitu  virhearvio hilalla 64")
    for nimi in ("psi", "u_min", "v_max", "v_min"):
        a, b, c = (getattr(t, nimi) for t in tulokset)
        p, raja, gci = richardson(a, b, c)
        print(f"  {nimi:8s} {p:8.2f} {raja:14.4f} {gci:12.4f}")
# @loppu hilat

# @alku reynolds
    teht, tila, _ = onkalo(400.0, 48, "AB2")
    t = tunnusluvut(teht, tila)
    print("Re = 400, hila 48")
    print(f"  psi_min {t.psi:.4f}, keskus ({t.keskus[0]:.3f}, "
          f"{t.keskus[1]:.3f}), u_min {t.u_min:.3f}")
# @loppu reynolds
