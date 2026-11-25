"""Elementtimenetelmän virhe kahdessa normissa.

Tehtävä -u'' = pi² sin(pi x), u(0) = u(1) = 0, tarkka ratkaisu
sin(pi x). Lineaarisilla elementeillä L2-virhe pienenee kuten h² ja
energianormin virhe (derivaatan virhe) kuten h."""

import math

import numpy as np
import numpy.typing as npt
from scipy.linalg import solve_banded

Taulukko = npt.NDArray[np.float64]

# Kolmen pisteen Gaussin kvadratuuri välillä [-1, 1].
GAUSS_X = np.array([-math.sqrt(0.6), 0.0, math.sqrt(0.6)])
GAUSS_W = np.array([5.0, 8.0, 5.0]) / 9.0


# @alku ratkaisu
def ratkaise(solmut: Taulukko) -> Taulukko:
    """Kokoaa ja ratkaisee; verkon ei tarvitse olla tasavälinen."""
    h = np.diff(solmut)
    n = len(solmut)
    nauha = np.zeros((3, n - 2))                 # sisäsolmut
    nauha[1, :] = 1.0 / h[:-1] + 1.0 / h[1:]
    nauha[0, 1:] = -1.0 / h[1:-1]
    nauha[2, :-1] = -1.0 / h[1:-1]
    f = np.zeros(n)
    for e in range(n - 1):                       # kuorma kvadratuurilla
        x = solmut[e] + 0.5 * h[e] * (GAUSS_X + 1.0)
        paino = 0.5 * h[e] * GAUSS_W * math.pi**2 * np.sin(math.pi * x)
        f[e] += float(np.sum(paino * (solmut[e + 1] - x) / h[e]))
        f[e + 1] += float(np.sum(paino * (x - solmut[e]) / h[e]))
    u = np.zeros(n)
    u[1:-1] = solve_banded((1, 1), nauha, f[1:-1])
    return u
# @loppu ratkaisu


# @alku normit
def virheet(solmut: Taulukko, u: Taulukko) -> tuple[float, float]:
    """L2-virhe ja energianormin virhe integroituna elementeittäin."""
    l2 = energia = 0.0
    for e in range(len(solmut) - 1):
        h = solmut[e + 1] - solmut[e]
        x = solmut[e] + 0.5 * h * (GAUSS_X + 1.0)
        uh = u[e] + (u[e + 1] - u[e]) * (x - solmut[e]) / h
        duh = (u[e + 1] - u[e]) / h
        l2 += float(np.sum(0.5 * h * GAUSS_W * (uh - np.sin(math.pi * x))**2))
        energia += float(np.sum(
            0.5 * h * GAUSS_W * (duh - math.pi * np.cos(math.pi * x))**2))
    return math.sqrt(l2), math.sqrt(energia)
# @loppu normit


# @alku taulukko
print("elementtejä   L2-virhe  kertaluku  energiavirhe  kertaluku")
ed_l2 = ed_en = 0.0
for n in (4, 8, 16, 32, 64):
    solmut = np.linspace(0.0, 1.0, n + 1)
    l2, en = virheet(solmut, ratkaise(solmut))
    p1 = f"{math.log2(ed_l2 / l2):9.2f}" if ed_l2 else "        -"
    p2 = f"{math.log2(ed_en / en):9.2f}" if ed_en else "        -"
    print(f"{n:11d} {l2:10.2e} {p1} {en:13.2e} {p2}")
    ed_l2, ed_en = l2, en

# Sama koodi epätasaisella verkolla: solmut tihenevät kohti reunoja.
t = np.linspace(0.0, 1.0, 33)
tihea = 0.5 * (1.0 - np.cos(math.pi * t))
l2, en = virheet(tihea, ratkaise(tihea))
print(f"32 epätasaista: L2 {l2:.2e}, energia {en:.2e}")
solmuvirhe = float(np.max(np.abs(ratkaise(solmut)
                                 - np.sin(math.pi * solmut))))
print("suurin virhe solmuissa (64 elementtiä): "
      + ("alle 1e-10" if solmuvirhe < 1e-10 else f"{solmuvirhe:.1e}"))
# @loppu taulukko
