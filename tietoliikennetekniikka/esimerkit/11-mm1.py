"""M/M/1-jono: simulaatio, kaava ja Littlen laki."""

import numpy as np

rng = np.random.default_rng(21)


# @alku lindley
def simuloi(kuorma: float, asiakkaita: int = 300_000) -> tuple[float, float]:
    """Palvelunopeus 1. Palauttaa keskimääräisen ajan järjestelmässä ja
    keskimääräisen määrän järjestelmässä (aikakeskiarvo)."""
    valit = rng.exponential(1 / kuorma, asiakkaita)
    palvelut = rng.exponential(1.0, asiakkaita)
    odotus = np.zeros(asiakkaita)
    for n in range(1, asiakkaita):       # Lindleyn rekursio
        odotus[n] = max(0.0, odotus[n - 1] + palvelut[n - 1] - valit[n])
    aika = odotus + palvelut
    kesto = float(valit.sum())
    return float(aika.mean()), float(aika.sum() / kesto)
# @loppu lindley


# @alku vertailu
print("  ρ    W sim  W=1/(μ-λ)   L sim  L=ρ/(1-ρ)  λ·W")
for rho in (0.5, 0.8, 0.9):
    w, n = simuloi(rho)
    print(f"{rho:>4} {w:>8.2f} {1 / (1 - rho):>10.2f} {n:>7.2f}"
          f" {rho / (1 - rho):>10.2f} {rho * w:>5.2f}")
# @loppu vertailu
