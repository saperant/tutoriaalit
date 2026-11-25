"""virta-kirjaston tarkistukset Taylorin ja Greenin pyörteellä.

Pyörre u = sin x cos y, v = -cos x sin y vaimenee kertoimella
exp(-2 nu t) ja toteuttaa Navier–Stokesin yhtälöt tarkasti. Neliössä
[0, pi] x [0, pi] sen reunat ovat symmetriatasoja."""

import math

import numpy as np

from virta import (
    Ratkaisija,
    Reuna,
    Taulukko,
    Tehtava,
    Tila,
    divergenssi,
    liike_energia,
)

NU = 0.1
LOPPU = 1.0


# @alku tarkka
def tehtava(n: int) -> Tehtava:
    liukuva = Reuna("liukuva")
    return Tehtava(n, n, math.pi, math.pi, NU, liukuva, liukuva, liukuva,
                   liukuva)


def tarkka(teht: Tehtava, t: float) -> tuple[Taulukko, Taulukko]:
    """Tarkka nopeus niissä pisteissä, joissa u ja v on tallennettu."""
    pinnat: Taulukko = np.linspace(0.0, math.pi, teht.nx + 1)
    kesket: Taulukko = (np.arange(teht.nx, dtype=np.float64) + 0.5) * teht.dx
    vaimennus = math.exp(-2.0 * NU * t)
    u = np.sin(pinnat)[:, None] * np.cos(kesket)[None, :] * vaimennus
    v = -np.cos(kesket)[:, None] * np.sin(pinnat)[None, :] * vaimennus
    return u, v
# @loppu tarkka


# @alku ajo
def aja(n: int, askelia: int, kaavio: str) -> tuple[Tehtava, Tila]:
    teht = tehtava(n)
    ratkaisija = Ratkaisija(teht)
    u, v = tarkka(teht, 0.0)
    tila = Tila(u, v, np.zeros((n, n)))
    for _ in range(askelia):
        tila = ratkaisija.askel(tila, LOPPU / askelia, kaavio)
    return teht, tila


def virhe(n: int, askelia: int, kaavio: str) -> float:
    teht, tila = aja(n, askelia, kaavio)
    u, _ = tarkka(teht, LOPPU)
    return float(np.max(np.abs(tila.u - u)))
# @loppu ajo


# @alku tarkistukset
teht, tila = aja(32, 100, "AB2")
print(f"suurin divergenssi alle 1e-12: "
      f"{bool(np.max(np.abs(divergenssi(teht, tila.u, tila.v))) < 1e-12)}")
alku = liike_energia(teht, *tarkka(teht, 0.0))
loppu = liike_energia(teht, tila.u, tila.v)
print(f"liike-energia lopussa / alussa: {loppu / alku:.4f}"
      f" (tarkka {math.exp(-4.0 * NU * LOPPU):.4f})")

print("paikan kertaluku (aika-askel niin pieni, ettei se vaikuta)")
print("  ruutuja/sivu  suurin virhe  kertaluku")
edellinen = 0.0
for n in (8, 16, 32, 64):
    e = virhe(n, 800, "AB2")
    p = f"{math.log2(edellinen / e):9.2f}" if edellinen else "        -"
    print(f"  {n:12d} {e:13.2e} {p}")
    edellinen = e

print("ajan kertaluku (16 ruutua/sivu, erotus tiheimpään ajoon)")
print("  askelia   Euler  kertaluku     AB2  kertaluku")
viite = {k: aja(16, 3200, k)[1].u for k in ("Euler", "AB2")}
ed = {"Euler": 0.0, "AB2": 0.0}
for askelia in (20, 40, 80, 160):
    rivi = f"  {askelia:7d}"
    for k in ("Euler", "AB2"):
        e = float(np.max(np.abs(aja(16, askelia, k)[1].u - viite[k])))
        p = f"{math.log2(ed[k] / e):9.2f}" if ed[k] else "        -"
        rivi += f" {e:8.1e} {p}"
        ed[k] = e
    print(rivi)
# @loppu tarkistukset
