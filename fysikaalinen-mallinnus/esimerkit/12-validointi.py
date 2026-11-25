"""Validointi: malli vastaan mittaus, ja kolme eri virhelähdettä.

"Mittaukset" on tässä tuotettu ohjelmallisesti rikkaammasta mallista
(konvektio ja säteily, lisäksi mittauskohina), koska oikeaa koetta ei
ole. Tarkasteltava malli tuntee vain konvektion."""

import numpy as np
import numpy.typing as npt
from scipy.integrate import solve_bvp
from scipy.linalg import solve_banded
from scipy.optimize import brentq

Taulukko = npt.NDArray[np.float64]

K, D, PITUUS = 45.0, 0.010, 0.300       # terästanko: W/(m K), m, m
T_ILMA = 20.0
ANTURIT = np.array([0.03, 0.06, 0.10, 0.15, 0.22, 0.29])
SIGMA, EMISSIIVISYYS, H_TOSI = 5.67e-8, 0.8, 9.0


# @alku koe
def koe(t_tyvi: float, siemen: int) -> Taulukko:
    """Koetta esittävä laskenta: konvektio + säteily + kohina 0,3 K."""
    def oikea(x: Taulukko, y: Taulukko) -> Taulukko:
        hukka = (H_TOSI * (y[0] - T_ILMA) + EMISSIIVISYYS * SIGMA
                 * ((y[0] + 273.15) ** 4 - (T_ILMA + 273.15) ** 4))
        return np.vstack([y[1], 4.0 * hukka / (K * D)])

    def reunat(ya: Taulukko, yb: Taulukko) -> Taulukko:
        return np.array([ya[0] - t_tyvi, yb[1]])      # kärki eristetty

    x = np.linspace(0.0, PITUUS, 50)
    alku = np.vstack([np.full(50, t_tyvi), np.zeros(50)])
    ratkaisu = solve_bvp(oikea, reunat, x, alku, tol=1e-8)
    kohina = np.random.default_rng(siemen).normal(0.0, 0.3, len(ANTURIT))
    tulos: Taulukko = ratkaisu.sol(ANTURIT)[0] + kohina
    return tulos
# @loppu koe


# @alku malli
def malli(h: float, t_tyvi: float, n: int = 300) -> Taulukko:
    """Tarkasteltava malli: pelkkä konvektio, differenssimenetelmä,
    haamupiste kärjessä. Palauttaa lämpötilat anturien kohdilla."""
    dx = PITUUS / n
    m2 = 4.0 * h / (K * D)
    nauha = np.zeros((3, n))
    nauha[0, 1:] = -1.0 / dx**2
    nauha[1, :] = 2.0 / dx**2 + m2
    nauha[2, :-1] = -1.0 / dx**2
    nauha[2, -2] = -2.0 / dx**2
    b = np.full(n, m2 * T_ILMA)
    b[0] += t_tyvi / dx**2
    u = np.concatenate(([t_tyvi], solve_banded((1, 1), nauha, b)))
    tulos: Taulukko = np.interp(ANTURIT, np.linspace(0.0, PITUUS, n + 1), u)
    return tulos
# @loppu malli


# @alku vertailu
mitattu = koe(100.0, siemen=1)
perus = malli(10.0, 100.0)
numeerinen = float(np.max(np.abs(perus - malli(10.0, 100.0, n=600))))
print(f"1. diskretointivirhe (n = 300 vs. 600): {numeerinen:.4f} K")
alin, ylin = malli(13.0, 100.0), malli(7.0, 100.0)
print("2. parametrin epävarmuus, käsikirja-arvo h = 10 ± 3 W/(m² K):")
print("   anturi mm   mitattu  malli h=10   vaihteluväli  mittaus välissä")
for i, paikka in enumerate(ANTURIT):
    sisalla = alin[i] - 0.3 <= mitattu[i] <= ylin[i] + 0.3
    print(f"{1e3 * paikka:12.0f} {mitattu[i]:9.1f} {perus[i]:11.1f} "
          f"{alin[i]:8.1f}–{ylin[i]:.1f} {'kyllä' if sisalla else 'ei':>13}")
# @loppu vertailu


# @alku kalibrointi
def derivaatta(h: float) -> float:
    """Jäännösneliösumman derivaatta h:n suhteen erotusosamääränä."""
    def nelio(arvo: float) -> float:
        return float(np.sum((malli(arvo, 100.0) - mitattu) ** 2))
    return (nelio(h + 1e-3) - nelio(h - 1e-3)) / 2e-3


def sateilyn_osuus(t_pinta: float) -> float:
    """Säteilyn osuus pinnan lämpöhäviöstä koetta esittävässä mallissa."""
    sateily = EMISSIIVISYYS * SIGMA * ((t_pinta + 273.15) ** 4
                                       - (T_ILMA + 273.15) ** 4)
    return sateily / (sateily + H_TOSI * (t_pinta - T_ILMA))


h_sovitettu = float(brentq(derivaatta, 5.0, 40.0))
jaannos = malli(h_sovitettu, 100.0) - mitattu
print(f"3. sovitettu h = {h_sovitettu:.1f} W/(m² K), jäännösten "
      f"keskihajonta {float(np.std(jaannos)):.2f} K (kohina 0,3 K)")

# Ennuste uudessa tilanteessa: tyvi 300 °C, sama sovitettu h.
ero = malli(h_sovitettu, 300.0) - koe(300.0, siemen=2)
print("4. ennuste, kun tyvi on 300 °C: malli - mittaus (K)")
print("   " + "  ".join(f"{e:5.1f}" for e in ero))
print(f"   keskimäärin {float(np.mean(ero)):.1f} K liian kuuma")
print(f"   säteilyn osuus häviöstä: 100 °C:ssa "
      f"{100 * sateilyn_osuus(100.0):.0f} %, 300 °C:ssa "
      f"{100 * sateilyn_osuus(300.0):.0f} %")
# @loppu kalibrointi
