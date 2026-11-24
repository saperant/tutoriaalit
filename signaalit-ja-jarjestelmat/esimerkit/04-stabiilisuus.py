"""BIBO-stabiilisuus: impulssivasteen itseisarvosumma ja pahin syöte."""

import numpy as np

# @alku stabiilisuus
n = np.arange(2_000)
vasteet = {
    "0.9^n u[n]": 0.9**n,
    "(-0.9)^n u[n]": (-0.9) ** n,
    "u[n] (summain)": np.ones(len(n)),
    "1/(n+1)": 1.0 / (n + 1),
    "1/(n+1)^2": 1.0 / (n + 1) ** 2,
}
for nimi, h in vasteet.items():
    osasummat = np.cumsum(np.abs(h))
    # Pahin rajoitettu syöte |x| <= 1: x[N-k] = sign(h[k]).
    pahin = np.sign(h[::-1])
    y_loppu = float(np.sum(h * pahin[::-1]))
    print(f"{nimi:<15} sum|h| 100: {osasummat[99]:7.2f}"
          f"  2000: {osasummat[-1]:7.2f}   pahin |y| {abs(y_loppu):7.2f}")
# @loppu stabiilisuus
