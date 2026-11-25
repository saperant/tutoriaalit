"""Äkisti liikkeelle lähtevä levy: liikemäärä leviää nesteeseen kuten
lämpö. Koko ketju taseesta tarkistukseen yhdessä tiedostossa."""

import math

import numpy as np
import numpy.typing as npt
from scipy.linalg import solve_banded
from scipy.special import erfc

Taulukko = npt.NDArray[np.float64]

# @alku malli
# Levy lähtee hetkellä 0 liikkeelle nopeudella U; neste on aluksi levossa.
U = 1.0            # levyn nopeus, m/s
NU = 1.0e-6        # veden kinemaattinen viskositeetti, m²/s
AIKA = 1.0         # tarkasteluhetki, s
KORKEUS = 0.02     # laskenta-alueen yläreuna, m (yli 10 rajakerrosta)


def tarkka(y: Taulukko, t: float, nu: float = NU) -> Taulukko:
    """Yhtälön u_t = nu u_yy samankaltaisuusratkaisu."""
    tulos: Taulukko = U * erfc(y / (2.0 * math.sqrt(nu * t)))
    return tulos
# @loppu malli


# @alku ratkaisu
def ratkaise(n: int, askelia: int) -> tuple[Taulukko, Taulukko]:
    """n kontrollitilavuutta, keskipisteet y; implisiittinen Euler.

    Tilavuuden i tase: h du/dt = vuo alapinnasta - vuo yläpinnasta,
    vuo = -nu du/dy. Levyn pinnassa etäisyys keskipisteeseen on h/2."""
    h = KORKEUS / n
    y: Taulukko = (np.arange(n, dtype=np.float64) + 0.5) * h
    r = NU * (AIKA / askelia) / h**2
    nauha = np.zeros((3, n))
    nauha[0, 1:] = -r
    nauha[2, :-1] = -r
    nauha[1, :] = 1.0 + 2.0 * r
    nauha[1, 0] = 1.0 + 3.0 * r        # seinä: vuo 2 nu (U - u_0) / h
    nauha[1, -1] = 1.0 + r             # yläreuna: ei leikkausta
    u: Taulukko = np.zeros(n)
    for _ in range(askelia):
        oikea = u.copy()
        oikea[0] += 2.0 * r * U
        u = solve_banded((1, 1), nauha, oikea)
    return y, u
# @loppu ratkaisu


# @alku tarkistus
print("tilavuuksia  askelia  suurin virhe m/s  virheiden suhde")
edellinen = 0.0
for n, askelia in ((50, 25), (100, 100), (200, 400), (400, 1600)):
    y, u = ratkaise(n, askelia)
    virhe = float(np.max(np.abs(u - tarkka(y, AIKA))))
    suhde = f"{edellinen / virhe:8.2f}" if edellinen else "       -"
    print(f"{n:11d} {askelia:8d} {virhe:17.2e} {suhde:>16}")
    edellinen = virhe
# @loppu tarkistus

# @alku paksuus
# Rajakerros: korkeus, jolla nopeus on pudonnut prosenttiin levyn
# nopeudesta. Samankaltaisuusratkaisusta delta = 3,64 sqrt(nu t).
print("neste (20 °C)   nu m²/s   rajakerros 1 s jälkeen")
for nimi, nu in (("ilma", 1.5e-5), ("vesi", 1.0e-6), ("glyseroli", 1.1e-3)):
    delta = 3.64 * math.sqrt(nu * AIKA)
    print(f"{nimi:12s} {nu:10.1e} {1e3 * delta:10.1f} mm")
# @loppu paksuus
