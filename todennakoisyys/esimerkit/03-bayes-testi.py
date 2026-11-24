"""Bayesin kaava: positiivinen testitulos ja harvinainen tila."""

import numpy as np


# @alku bayes
def p_sairas_kun_positiivinen(esiintyvyys: float, herkkyys: float,
                              tarkkuus: float) -> float:
    """P(sairas | positiivinen) Bayesin kaavalla."""
    tosi_pos = herkkyys * esiintyvyys
    vaara_pos = (1 - tarkkuus) * (1 - esiintyvyys)
    return tosi_pos / (tosi_pos + vaara_pos)


for esiintyvyys in (0.001, 0.01, 0.1):
    p = p_sairas_kun_positiivinen(esiintyvyys, herkkyys=0.99,
                                  tarkkuus=0.95)
    print(f"esiintyvyys {esiintyvyys:5.1%}: P(sairas | +) = {p:.3f}")
# @loppu bayes

# @alku simulointi
rng = np.random.default_rng(11)
n = 1_000_000
sairas = rng.random(n) < 0.01
positiivinen = np.where(sairas, rng.random(n) < 0.99,
                        rng.random(n) < 0.05)
print(f"simulointi: {int(positiivinen.sum())} positiivista, joista"
      f" sairaita {float(sairas[positiivinen].mean()):.3f}")
# @loppu simulointi

# @alku halytys
# Valvonta: hälytin havaitsee vian 95 %:n varmuudella, mutta hälyttää
# turhaan 1 %:ssa tunneista. Vika on 1 tunnissa 1000:sta.
p = p_sairas_kun_positiivinen(0.001, herkkyys=0.95, tarkkuus=0.99)
print(f"hälytys: P(oikea vika | hälytys) = {p:.3f}")
# @loppu halytys
