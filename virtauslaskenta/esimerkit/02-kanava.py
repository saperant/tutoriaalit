"""Voitelukalvo: liikkuva levy ja painegradientti yhtä aikaa.

Täysin kehittyneessä virtauksessa nopeus riippuu vain korkeudesta y, ja
liikemäärän tase supistuu muotoon d/dy (mu du/dy) = dp/dx."""

import math
from collections.abc import Callable

import numpy as np
import numpy.typing as npt
from scipy.integrate import quad
from scipy.linalg import solve_banded

Taulukko = npt.NDArray[np.float64]

# @alku tehtava
RAKO = 50e-6        # kalvon paksuus H, m
U_LEVY = 5.0        # alalevyn nopeus, m/s; ylälevy on paikallaan
MU0 = 0.03          # öljyn viskositeetti kylmänä, Pa s
GRADIENTTI = -2e8   # dp/dx, Pa/m: paine laskee virtaussuuntaan


def vakio(y: float) -> float:
    return MU0


def lampeneva(y: float) -> float:
    """Liikkuva levy on kuuma: viskositeetti on siellä kolmasosa."""
    return MU0 * math.exp(-math.log(3.0) * (1.0 - y / RAKO))
# @loppu tehtava


# @alku ratkaisu
def ratkaise(n: int, mu: Callable[[float], float]
             ) -> tuple[Taulukko, Taulukko, Taulukko]:
    """n kontrollitilavuutta raon poikki. Palauttaa keskipisteet,
    nopeudet ja leikkausjännitykset pinnoilla (n + 1 kappaletta)."""
    h = RAKO / n
    y: Taulukko = (np.arange(n, dtype=np.float64) + 0.5) * h
    # Viskositeetti tilavuuksien välisillä pinnoilla ja seinillä.
    pinnat = np.array([mu(j * h) for j in range(n + 1)])
    johto = pinnat / h                   # pinnan "johtavuus" mu / etäisyys
    johto[0] *= 2.0                      # seinään on matkaa vain h / 2
    johto[-1] *= 2.0
    nauha = np.zeros((3, n))
    nauha[0, 1:] = -johto[1:-1]
    nauha[2, :-1] = -johto[1:-1]
    nauha[1, :] = johto[:-1] + johto[1:]
    oikea = np.full(n, -GRADIENTTI * h)  # painevoima tilavuuteen
    oikea[0] += johto[0] * U_LEVY        # alaseinän nopeus tunnetaan
    u: Taulukko = solve_banded((1, 1), nauha, oikea)
    # Leikkausjännitys tau = mu du/dy jokaisella pinnalla.
    laajennettu = np.concatenate(([U_LEVY], u, [0.0]))
    tau: Taulukko = johto * np.diff(laajennettu)
    return y, u, tau
# @loppu ratkaisu


# @alku tarkka
def tarkka(y: float, mu: Callable[[float], float]) -> float:
    """tau(y) = tau_0 + dp/dx y, joten u' = tau / mu integroidaan.
    Vakio tau_0 määräytyy ehdosta u(H) = 0."""
    a = quad(lambda s: 1.0 / mu(s), 0.0, RAKO)[0]
    b = quad(lambda s: s / mu(s), 0.0, RAKO)[0]
    tau0 = -(U_LEVY + GRADIENTTI * b) / a
    osa = quad(lambda s: (tau0 + GRADIENTTI * s) / mu(s), 0.0, y)[0]
    return float(U_LEVY + osa)
# @loppu tarkka


# @alku vertailu
for nimi, mu in (("vakioviskositeetti", vakio),
                 ("lämpenevä öljy", lampeneva)):
    print(nimi)
    print("  tilavuuksia  suurin virhe m/s  suhde  voimatase")
    edellinen = 0.0
    for n in (10, 20, 40, 80):
        y, u, tau = ratkaise(n, mu)
        virhe = max(abs(u[j] - tarkka(float(y[j]), mu)) for j in range(n))
        suhde = f"{edellinen / virhe:6.2f}" if edellinen else "     -"
        # Seinien leikkausvoimien erotus kumoaa painevoiman dp/dx H.
        tase = tau[-1] - tau[0] - GRADIENTTI * RAKO
        kunnossa = abs(tase) < 1e-9 * abs(GRADIENTTI * RAKO)
        print(f"  {n:11d} {virhe:17.2e} {suhde}  "
              f"{'toteutuu' if kunnossa else 'EI TOTEUDU'}")
        edellinen = virhe
    y, u, tau = ratkaise(80, mu)
    virtaama = float(np.sum(u)) * RAKO / 80
    print(f"  tilavuusvirta {1e6 * virtaama:.1f} mm²/s, "
          f"leikkausjännitys liikkuvalla levyllä {tau[0] / 1e3:+.2f} kPa")
# @loppu vertailu
