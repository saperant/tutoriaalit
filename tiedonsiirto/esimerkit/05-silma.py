"""Silmäkuvion aukeama ajoitusvirheen funktiona eri roll-off-kertoimilla."""

import numpy as np

sps, janne = 16, 24
t = np.arange(-janne * sps // 2, janne * sps // 2 + 1) / sps


def korotettu_kosini(beta: float) -> np.ndarray:
    if beta == 0:
        return np.sinc(t)
    nimittaja = 1 - (2 * beta * t) ** 2
    raja = np.isclose(nimittaja, 0.0)
    p = np.sinc(t) * np.cos(np.pi * beta * t) / np.where(raja, 1.0, nimittaja)
    return np.where(raja, np.pi / 4 * np.sinc(1 / (2 * beta)), p)


# @alku aukeama
rng = np.random.default_rng(7)
symbolit = 1.0 - 2 * rng.integers(0, 2, 4_000)   # BPSK, +-1
nostettu = np.zeros(len(symbolit) * sps)
nostettu[::sps] = symbolit
print("ajoitusvirhe   beta = 0   beta = 0.35   beta = 1")
for siirto in (0, 1, 2, 4):                   # näytteinä, sps = 16
    rivi = []
    for beta in (0.0, 0.35, 1.0):
        y = np.convolve(nostettu, korotettu_kosini(beta))
        alku = janne * sps // 2 + siirto
        naytteet = y[alku::sps][janne: len(symbolit) - janne]
        mukana = symbolit[janne: len(symbolit) - janne]
        # Pystysuora aukeama: pienin etäisyys päätösrajasta (nollasta).
        rivi.append(float(np.min(naytteet * mukana)))
    print(f"{siirto / sps:8.4f} T   " + "   ".join(f"{a:8.3f}" for a in rivi))
# @loppu aukeama
