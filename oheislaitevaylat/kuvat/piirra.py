#!/usr/bin/env python3
"""Piirtää luvun 2 kuvan vetovastuksen vaikutuksesta nousuaikaan
(make kuvat).

Suurin sallittu vastus luetaan esimerkin avokollektori.py testatusta
tulosteesta, joten kuva ja taulukko perustuvat samaan laskelmaan.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

TAALLA = Path(__file__).resolve().parent
TULOSTE = TAALLA.parent / "esimerkit" / "python" / "avokollektori.odotettu"
MUSTE = "#1F2A2E"
VARIT = ["#0D7A6C", "#B8860B", "#B4472E"]

VDD = 3.3
CB_PF = 200
TR_NS = 300            # Fast-moodin raja 30 % -> 70 %


def rajat() -> tuple[float, float]:
    """Rp min ja max riviltä "Fast 400 kHz ... 200"."""
    for rivi in TULOSTE.read_text(encoding="utf-8").splitlines():
        if osuma := re.match(rf"Fast 400 kHz\s+{CB_PF}\s+(\d+)R\s+(\d+)R",
                             rivi):
            return float(osuma[1]), float(osuma[2])
    raise SystemExit("avokollektori.odotettu: riviä ei löytynyt")


def main() -> None:
    rp_min, rp_max = rajat()
    nousu = math.log(0.7 / 0.3)
    if abs(nousu * rp_max * CB_PF * 1e-3 - TR_NS) > 1:
        raise SystemExit("taulukon Rp max ei vastaa nousuajan kaavaa")
    t = np.linspace(0.0, 1250.0, 1000)             # ns: puoli jaksoa
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    vastukset = [(rp_min, "pienin sallittu"), (rp_max, "suurin sallittu"),
                 (4700.0, "liian suuri")]
    for (rp, kuvaus), vari in zip(vastukset, VARIT):
        tau = rp * CB_PF * 1e-3                    # ns
        ax.plot(t, VDD * (1 - np.exp(-t / tau)), color=vari, linewidth=1.5,
                label=f"{rp / 1000:.2f} kΩ ({kuvaus}): "
                      f"nousuaika {nousu * tau:.0f} ns".replace(".", ","))
    for osuus in (0.3, 0.7):
        ax.axhline(osuus * VDD, color=MUSTE, linewidth=0.6, linestyle="--")
        ax.text(1255, osuus * VDD, f"{osuus:.0%}".replace("%", " %"),
                va="center", fontsize=8, color=MUSTE)
    ax.set_xlim(0, 1250)
    ax.set_ylim(0, VDD * 1.05)
    ax.set_xlabel("aika linjan vapauttamisesta (ns)", color=MUSTE)
    ax.set_ylabel("SCL (V)", color=MUSTE)
    ax.legend(loc="lower right", fontsize=8, frameon=False)
    for reuna in ("top", "right"):
        ax.spines[reuna].set_visible(False)
    fig.tight_layout()
    fig.savefig(TAALLA / "nousuaika.png", dpi=200)


if __name__ == "__main__":
    main()
