"""Miksi paine ja nopeus tallennetaan eri paikkoihin.

Jos paine ja nopeus ovat samoissa pisteissä ja painegradientti lasketaan
keskeisdifferenssillä, ruudun oma paine ei vaikuta siihen lainkaan.
Shakkilautakuvioinen painekenttä jää silloin kokonaan näkymättömäksi."""

import numpy as np
import numpy.typing as npt

Taulukko = npt.NDArray[np.float64]

# @alku kentta
N = 8
H = 1.0 / N
i, j = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
shakki: Taulukko = np.where((i + j) % 2 == 0, 1.0, -1.0)
# @loppu kentta


# @alku gradientit
def sama_piste(p: Taulukko) -> Taulukko:
    """dp/dx ruudun keskellä naapureista (jaksollinen alue)."""
    tulos: Taulukko = (np.roll(p, -1, axis=0)
                       - np.roll(p, 1, axis=0)) / (2 * H)
    return tulos


def porrastettu(p: Taulukko) -> Taulukko:
    """dp/dx ruutujen välisellä pinnalla, jossa nopeus u sijaitsee."""
    tulos: Taulukko = (p - np.roll(p, 1, axis=0)) / H
    return tulos


print("shakkilautapaine, vaihteluväli -1 … 1")
for nimi, gradientti in (("samoissa pisteissä", sama_piste),
                         ("pinnoilla", porrastettu)):
    suurin = float(np.max(np.abs(gradientti(shakki))))
    print(f"  gradientti {nimi}: suurin {suurin:.1f}")
# @loppu gradientit


# @alku nolla-avaruus
def laplace(tapa: str) -> Taulukko:
    """Paineyhtälön matriisi div(grad p) tiheänä: sarake kerrallaan."""
    a = np.zeros((N * N, N * N))
    for k in range(N * N):
        p = np.zeros(N * N)
        p[k] = 1.0
        p2 = p.reshape(N, N)
        if tapa == "sama piste":
            gx, gy = sama_piste(p2), sama_piste(p2.T).T
            div = sama_piste(gx) + sama_piste(gy.T).T
        else:
            gx, gy = porrastettu(p2), porrastettu(p2.T).T
            # Divergenssi ruudussa: oikea pinta miinus vasen pinta.
            div = ((np.roll(gx, -1, axis=0) - gx)
                   + (np.roll(gy, -1, axis=1) - gy)) / H
        a[:, k] = div.ravel()
    return a


for tapa in ("sama piste", "porrastettu"):
    ominaisarvot = np.linalg.eigvalsh(laplace(tapa))
    nollia = int(np.sum(np.abs(ominaisarvot) < 1e-8))
    print(f"paineyhtälö, {tapa}: {nollia} painekenttää, joita yhtälö ei näe")
# @loppu nolla-avaruus
