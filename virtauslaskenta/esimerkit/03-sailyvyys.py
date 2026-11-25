"""Säilyvä ja säilymätön diskretointi advektiolle.

Aine kulkeutuu virtauksessa, jonka nopeus hidastuu matkalla (kanava
levenee). Säilyvässä muodossa jokainen pinnan läpi kulkeva määrä
vähennetään yhdestä tilavuudesta ja lisätään seuraavaan."""

import numpy as np
import numpy.typing as npt

Taulukko = npt.NDArray[np.float64]

# @alku tehtava
PITUUS = 1.2
N = 60
H = PITUUS / N
DT = 0.004
ASKELIA = 150
KESKET: Taulukko = (np.arange(N, dtype=np.float64) + 0.5) * H
PINNAT: Taulukko = np.arange(N + 1, dtype=np.float64) * H


def nopeus(x: Taulukko) -> Taulukko:
    """Virtaus hidastuu arvosta 1,5 arvoon 0,5."""
    tulos: Taulukko = 1.0 - 0.5 * np.tanh((x - 0.5) / 0.1)
    return tulos


def alkutila() -> Taulukko:
    tulos: Taulukko = np.exp(-(((KESKET - 0.25) / 0.06) ** 2))
    return tulos
# @loppu tehtava


# @alku sailyva
def sailyva_askel(c: Taulukko) -> Taulukko:
    """dc/dt + d(uc)/dx = 0: vuo jokaisella pinnalla kerran."""
    u = nopeus(PINNAT)
    vuo = np.zeros(N + 1)
    vuo[1:] = u[1:] * c              # vastavirta: arvo tulee vasemmalta
    uusi: Taulukko = c - DT / H * (vuo[1:] - vuo[:-1])
    return uusi
# @loppu sailyva


# @alku sailymaton
def sailymaton_askel(c: Taulukko) -> Taulukko:
    """Sama yhtälö auki kerrottuna: dc/dt + u dc/dx + c du/dx = 0."""
    u = nopeus(KESKET)
    dudx = (nopeus(PINNAT[1:]) - nopeus(PINNAT[:-1])) / H
    dcdx = np.zeros(N)
    dcdx[1:] = (c[1:] - c[:-1]) / H
    dcdx[0] = c[0] / H
    uusi: Taulukko = c - DT * (u * dcdx + c * dudx)
    return uusi
# @loppu sailymaton


# @alku ajo
def aja() -> tuple[Taulukko, Taulukko, list[tuple[float, float]]]:
    a = alkutila()
    b = alkutila()
    maarat = [(float(np.sum(a)) * H, float(np.sum(b)) * H)]
    for _ in range(ASKELIA):
        a, b = sailyva_askel(a), sailymaton_askel(b)
        maarat.append((float(np.sum(a)) * H, float(np.sum(b)) * H))
    return a, b, maarat


if __name__ == "__main__":
    a, b, maarat = aja()
    alku = maarat[0][0]
    print("askel  aika   säilyvä muoto  auki kerrottu")
    for k in (0, 50, 100, 150):
        print(f"{k:5d} {k * DT:5.2f} {maarat[k][0] / alku:14.4f}"
              f" {maarat[k][1] / alku:14.4f}")
    print(f"huippu lopussa: säilyvä {float(np.max(a)):.3f}, "
          f"auki kerrottu {float(np.max(b)):.3f}")
# @loppu ajo
