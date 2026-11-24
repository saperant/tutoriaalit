"""Kuvaajan piirtäminen tiedostoon Matplotlibilla."""

from pathlib import Path

import numpy as np
from matplotlib.figure import Figure

# @alku kuvaaja
x = np.linspace(-2.0, 4.0, 400)
fig = Figure(figsize=(5.0, 3.0), layout="constrained")
ax = fig.add_subplot()
ax.plot(x, x**2 - 2 * x - 3, label="f(x) = x^2 - 2x - 3")
ax.axhline(0.0, color="gray", linewidth=0.8)
ax.plot([-1.0, 3.0], [0.0, 0.0], "o", label="nollakohdat")
ax.set(xlabel="x", ylabel="y", title="Paraabeli")
ax.grid(True, alpha=0.3)
ax.legend()
polku = Path("paraabeli.png")
fig.savefig(polku, dpi=150)
# @loppu kuvaaja

print("tallennettu:", polku.name, polku.exists())
print("viivoja:", len(ax.lines))
print("x-akseli:", [round(float(v), 2) for v in ax.get_xlim()])
