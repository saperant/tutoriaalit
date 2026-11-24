"""Suotimen vaatimukset tietona ja niiden tarkistus."""

from dataclasses import dataclass

import numpy as np
from scipy import signal


# @alku vaatimus
@dataclass(frozen=True)
class Alipaasto:
    """Alipaastosuotimen vaatimukset; taajuudet hertseina."""

    fs: float
    paasto: float          # paastokaistan yläraja
    esto: float            # estokaistan alaraja
    aaltoilu_db: float     # suurin sallittu huipusta huippuun
    vaimennus_db: float    # pienin sallittu vaimennus

    def __post_init__(self) -> None:
        if not 0 < self.paasto < self.esto < self.fs / 2:
            raise ValueError("vaatimus: 0 < paasto < esto < fs/2")
# @loppu vaatimus


# @alku tarkista
def tarkista(b: np.ndarray, a: np.ndarray, v: Alipaasto) -> list[str]:
    """Palauttaa rikotut vaatimukset; tyhja lista = kunnossa."""
    f, H = signal.freqz(b, a, worN=32_768, fs=v.fs)
    db = 20 * np.log10(np.maximum(np.abs(H), 1e-15))
    kaista = db[f <= v.paasto]
    aaltoilu = float(kaista.max() - kaista.min())
    vaimennus = float(-db[f >= v.esto].max())
    rikkeet = []
    if aaltoilu > v.aaltoilu_db:
        rikkeet.append(f"aaltoilu {aaltoilu:.3f} > {v.aaltoilu_db} dB")
    if vaimennus < v.vaimennus_db:
        rikkeet.append(f"vaimennus {vaimennus:.1f} < {v.vaimennus_db} dB")
    if abs(kaista.max()) > v.aaltoilu_db:
        rikkeet.append(f"vahvistus {kaista.max():.3f} dB, ei 0 dB")
    return rikkeet
# @loppu tarkista


# @alku kaytto
v = Alipaasto(fs=8_000.0, paasto=1_000.0, esto=1_500.0,
              aaltoilu_db=0.1, vaimennus_db=60.0)
for lkm in (41, 61):
    h = signal.firwin(lkm, 1_250.0, window=("kaiser", 5.653), fs=v.fs)
    rikkeet = tarkista(h, np.array([1.0]), v)
    print(f"{lkm} kerrointa:", "; ".join(rikkeet) or "kunnossa")
try:
    Alipaasto(fs=8_000.0, paasto=1_000.0, esto=5_000.0,
              aaltoilu_db=0.1, vaimennus_db=60.0)
except ValueError as virhe:
    print("hylatty:", virhe)
# @loppu kaytto
