"""Aika-askeleen rajat: Eulerin menetelmä ja Adams–Bashforth.

Kaksi sisäkkäistä pyörrettä lähes kitkattomassa nesteessä. Liike-energia
voi vain pienentyä; jos se kasvaa, kasvu on numeerista."""

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
    Tila,
    liike_energia,
)

# @alku tehtava
N = 32
NU = 2e-4
LOPPU = 12.0


def alkutila(teht: Tehtava) -> tuple[Taulukko, Taulukko]:
    """Suuri pyörre ja sen päällä neljä kertaa pienempi, heikompi."""
    pinnat: Taulukko = np.linspace(0.0, math.pi, teht.nx + 1)
    kesket: Taulukko = (np.arange(teht.nx, dtype=np.float64) + 0.5) * teht.dx
    u = np.zeros((teht.nx + 1, teht.ny))
    v = np.zeros((teht.nx, teht.ny + 1))
    for k, a in ((1, 1.0), (4, 0.1)):
        u += a * np.sin(k * pinnat)[:, None] * np.cos(k * kesket)[None, :]
        v -= a * np.cos(k * kesket)[:, None] * np.sin(k * pinnat)[None, :]
    return u, v


def energia_lopussa(dt: float, kaavio: str) -> float:
    """Liike-energia hetkellä LOPPU suhteessa alkuun; nan, jos lasku
    hajoaa."""
    liukuva = Reuna("liukuva")
    teht = Tehtava(N, N, math.pi, math.pi, NU, liukuva, liukuva, liukuva,
                   liukuva)
    ratkaisija = Ratkaisija(teht)
    u, v = alkutila(teht)
    alku = liike_energia(teht, u, v)
    tila = Tila(u, v, np.zeros((N, N)))
    with np.errstate(all="ignore"):
        for _ in range(round(LOPPU / dt)):
            tila = ratkaisija.askel(tila, dt, kaavio)
    return liike_energia(teht, tila.u, tila.v) / alku
# @loppu tehtava


# @alku taulukko
h = math.pi / N
print(f"viite (AB2, dt = 0,002): {energia_lopussa(0.002, 'AB2'):.3f}")
print("kaavio     dt   Courant  dt / (2 nu / U²)  energia lopussa / alussa")
for kaavio, dt in (("Euler", 0.005), ("Euler", 0.01),
                   ("Euler", 0.02), ("AB2", 0.02), ("AB2", 0.04),
                   ("AB2", 0.08)):
    e = energia_lopussa(dt, kaavio)
    tulos = f"{e:.3f}" if math.isfinite(e) and e < 10.0 else "hajoaa"
    print(f"{kaavio:6s} {dt:6.3f} {dt / h:8.2f} {dt / (2.0 * NU):14.1f}"
          f" {tulos:>18}")
# @loppu taulukko
