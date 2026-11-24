"""Aika-taajuusepätarkkuus."""

import math
from typing import Any

import numpy as np
from numpy.typing import NDArray

Taulukko = NDArray[np.floating[Any]]


# @alku epatarkkuus
def leveys_aika(x: Taulukko, t: Taulukko) -> float:
    p = x**2 / np.sum(x**2)                  # |x|^2 todennäköisyytenä
    keski = np.sum(t * p)
    return math.sqrt(float(np.sum((t - keski) ** 2 * p)))


def leveys_taajuus(x: Taulukko, dt: float) -> float:
    """sigma_f^2 = int |x'|^2 / (4 pi^2 int |x|^2) (Parseval)."""
    derivaatta = np.gradient(x, dt)
    return math.sqrt(float(np.sum(derivaatta**2) / np.sum(x**2))) / (2
                                                                      * np.pi)


dt = 0.001
t = np.arange(-30000, 30001) * dt            # [-30, 30]
pulssit = {
    "Gauss, s = 0.2": np.exp(-(t**2) / (2 * 0.2**2)),
    "Gauss, s = 2": np.exp(-(t**2) / (2 * 2.0**2)),
    "e^(-|t|)": np.exp(-np.abs(t)),
    "Hann-pulssi": np.where(np.abs(t) <= 0.5, (1 + np.cos(2 * np.pi * t))
                            / 2, 0.0),
}
print(f"alaraja 1/(4 pi) = {1 / (4 * math.pi):.4f}")
print("pulssi            sigma_t   sigma_f   tulo")
for nimi, x in pulssit.items():
    st, sf = leveys_aika(x, t), leveys_taajuus(x, dt)
    print(f"{nimi:16s} {st:8.4f} {sf:9.4f} {st * sf:7.4f}")
# @loppu epatarkkuus
