"""Valmistetun ratkaisun menetelmä: koodin tarkistus ilman tunnettua
ratkaisua.

Tehtävä -(k(x) u')' + c u = f välillä (0, 1). Ratkaisu keksitään,
SymPy johtaa siitä lähdetermin f, ja ratkaisijan pitää palauttaa keksitty
ratkaisu oikealla kertaluvulla. Mukana on tahallinen virhe."""

import math

import numpy as np
import numpy.typing as npt
import sympy as sym
from scipy.linalg import solve_banded

Taulukko = npt.NDArray[np.float64]

# @alku valmistus
X = sym.Symbol("x")
K_LAUSEKE = 1 + X**2                      # johtavuus vaihtelee paikan mukaan
C_VAKIO = 3
U_LAUSEKE = sym.sin(3 * X) * sym.exp(X)   # keksitty ratkaisu
F_LAUSEKE = (-sym.diff(K_LAUSEKE * sym.diff(U_LAUSEKE, X), X)
             + C_VAKIO * U_LAUSEKE)
k_funktio = sym.lambdify(X, K_LAUSEKE, "numpy")
u_funktio = sym.lambdify(X, U_LAUSEKE, "numpy")
f_funktio = sym.lambdify(X, sym.simplify(F_LAUSEKE), "numpy")
# @loppu valmistus


# @alku ratkaisija
def ratkaise(n: int, virhe: bool) -> tuple[Taulukko, Taulukko]:
    """Säilyvä differenssikaava: johtavuus välien keskipisteissä.
    Virheellisessä versiossa oikean puolen johtavuus otetaan solmusta."""
    h = 1.0 / n
    x = np.linspace(0.0, 1.0, n + 1)
    k_vasen = k_funktio(x[1:-1] - 0.5 * h)
    k_oikea = k_funktio(x[1:-1] if virhe else x[1:-1] + 0.5 * h)
    nauha = np.zeros((3, n - 1))
    nauha[0, 1:] = -k_oikea[:-1] / h**2
    nauha[1, :] = (k_vasen + k_oikea) / h**2 + C_VAKIO
    nauha[2, :-1] = -k_vasen[1:] / h**2
    b = np.asarray(f_funktio(x[1:-1]), dtype=np.float64)
    reuna0, reuna1 = float(u_funktio(0.0)), float(u_funktio(1.0))
    b[0] += k_vasen[0] * reuna0 / h**2
    b[-1] += k_oikea[-1] * reuna1 / h**2
    u = np.empty(n + 1)
    u[0], u[-1] = reuna0, reuna1
    u[1:-1] = solve_banded((1, 1), nauha, b)
    return x, u
# @loppu ratkaisija


# @alku kertaluku
print(f"lähdetermissä on {len(sym.Add.make_args(sym.expand(F_LAUSEKE)))}"
      " termiä; SymPy johti sen")
print("    n  oikea koodi  kertaluku  virheellinen  kertaluku")
ed = [0.0, 0.0]
for n in (10, 20, 40, 80, 160):
    rivi = f"{n:5d}"
    for i, bugi in enumerate((False, True)):
        x, u = ratkaise(n, bugi)
        e = float(np.max(np.abs(u - u_funktio(x))))
        p = f"{math.log2(ed[i] / e):9.2f}" if ed[i] else "        -"
        rivi += f" {e:12.2e} {p}"
        ed[i] = e
    print(rivi)
# @loppu kertaluku
