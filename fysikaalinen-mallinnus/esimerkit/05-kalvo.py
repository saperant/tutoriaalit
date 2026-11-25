"""Neliön muotoinen kalvo: ominaistaajuudet aikasimulaatiosta.

Kalvo (sivu 1, aallon nopeus 1) kiinni reunoiltaan. Keskelle tehdään
pieni kuoppa, päästetään irti ja mitataan keskipisteen liike.
Tarkat ominaistaajuudet ovat f = sqrt(m² + n²) / 2."""

import math

import numpy as np
import numpy.typing as npt

Taulukko = npt.NDArray[np.float64]
N = 64                      # välejä suuntaansa
C = 0.5                     # Courantin luku; raja on 1/sqrt(2)
KESTO = 40.0


# @alku simulointi
def laplace(u: Taulukko) -> Taulukko:
    tulos = np.zeros_like(u)
    tulos[1:-1, 1:-1] = (u[2:, 1:-1] + u[:-2, 1:-1] + u[1:-1, 2:]
                         + u[1:-1, :-2] - 4.0 * u[1:-1, 1:-1])
    return tulos


def simuloi() -> tuple[Taulukko, float]:
    """Palauttaa keskipisteen poikkeaman aikasarjana ja aika-askeleen."""
    h = 1.0 / N
    dt = C * h
    x = np.linspace(0.0, 1.0, N + 1)
    xx, yy = np.meshgrid(x, x)
    vanha = np.exp(-((xx - 0.5) ** 2 + (yy - 0.5) ** 2) / 0.01)
    vanha[0, :] = vanha[-1, :] = vanha[:, 0] = vanha[:, -1] = 0.0
    u = vanha + 0.5 * C * C * laplace(vanha)
    askelia = round(KESTO / dt)
    keski = np.empty(askelia)
    for k in range(askelia):
        u, vanha = 2.0 * u - vanha + C * C * laplace(u), u
        keski[k] = u[N // 2, N // 2]
    return keski, dt
# @loppu simulointi


# @alku spektri
def huiput(sarja: Taulukko, dt: float) -> list[float]:
    """Spektrin huiput, jotka ovat vähintään 2 % korkeimmasta. Ikkunan
    sivukeilat karsitaan: huipun lähellä (0,15) ei saa olla korkeampaa."""
    ikkuna = np.hanning(len(sarja))
    pituus = 8 * len(sarja)                       # nollilla täyttö
    spektri = np.abs(np.fft.rfft(sarja * ikkuna, pituus))
    taajuudet = np.fft.rfftfreq(pituus, dt)
    raja = 0.02 * float(spektri.max())
    ehdokkaat = [i for i in range(1, len(spektri) - 1)
                 if spektri[i - 1] < spektri[i] > spektri[i + 1]
                 and spektri[i] > raja and taajuudet[i] < 3.0]
    hyvaksytyt: list[int] = []
    for i in sorted(ehdokkaat, key=lambda i: -spektri[i]):
        if all(abs(taajuudet[i] - taajuudet[j]) > 0.15 for j in hyvaksytyt):
            hyvaksytyt.append(i)
    return sorted(float(taajuudet[i]) for i in hyvaksytyt)


sarja, dt = simuloi()
print("moodi (m, n)  tarkka f  mitattu f  ero %")
# Keskelle tehty symmetrinen kuoppa herättää vain moodit, joissa m ja n
# ovat parittomia.
moodit = [(1, 1), (1, 3), (3, 3), (1, 5), (3, 5)]
for (m, n), f in zip(moodit, huiput(sarja, dt), strict=True):
    tarkka = math.sqrt(m * m + n * n) / 2.0
    print(f"({m}, {n}) {tarkka:15.4f} {f:10.4f} "
          f"{100.0 * (f - tarkka) / tarkka:6.2f}")
# @loppu spektri
