#!/usr/bin/env python3
"""Piirtää luvun 8 periaatekuvan virrankulutuksesta (make kuvat).

Virrat ovat luvun taulukon suuruusluokkia tyypilliselle piirille,
eivät mittauksia. Skripti tulostaa myös keskivirrat ja pariston
keston, jotka ovat luvun taulukossa.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

TAALLA = Path(__file__).resolve().parent
MUSTE = "#1F2A2E"
VARIT = ["#B4472E", "#B8860B", "#0D7A6C"]

AJO_A = 5e-3          # 25 MHz:n ajo
UNI_A = 1.5e-3        # prosessorin kello pysäytetty
SYVA_UNI_A = 3e-6     # nopeat kellot pysäytetty, RTC käy
JAKSO_S = 1.0         # mittaus kerran sekunnissa
TYO_S = 5e-3          # mittaus ja lähetys
PARISTO_AH = 0.220    # CR2032


def keskivirta(lepo_a: float) -> float:
    return (AJO_A * TYO_S + lepo_a * (JAKSO_S - TYO_S)) / JAKSO_S


def kesto(virta_a: float) -> str:
    tunnit = PARISTO_AH / virta_a
    if tunnit < 72:
        return f"{tunnit:.0f} tuntia"
    if tunnit < 24 * 60:
        return f"{tunnit / 24:.0f} vuorokautta"
    return f"{tunnit / 24 / 30.4:.0f} kuukautta"


def main() -> None:
    tavat = [("kiireinen odotus", AJO_A), ("uni, tikki 1 ms", UNI_A),
             ("syvä uni ja RTC-herätys", SYVA_UNI_A)]
    t = np.linspace(0.0, 2.2, 4401)
    tyossa = (t % JAKSO_S) < TYO_S
    fig, ax = plt.subplots(figsize=(7.0, 3.1))
    for (nimi, lepo), vari in zip(tavat, VARIT):
        virta = np.where(tyossa, AJO_A, lepo)
        ka = keskivirta(lepo)
        print(f"{nimi}: keskivirta {ka * 1e6:.0f} µA, {kesto(ka)}")
        ax.step(t, virta * 1e6, where="post", color=vari, linewidth=1.4,
                label=f"{nimi}: {ka * 1e6:,.0f} µA".replace(",", " "))
    ax.set_yscale("log")
    ax.set_ylim(1, 2e4)
    ax.set_xlabel("aika (s)", color=MUSTE)
    ax.set_ylabel("virta (µA)", color=MUSTE)
    ax.grid(True, which="major", color="#D9E0E3", linewidth=0.6)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=3,
              fontsize=7, frameon=False, columnspacing=1.2,
              handlelength=1.5)
    for reuna in ("top", "right"):
        ax.spines[reuna].set_visible(False)
    fig.tight_layout()
    fig.savefig(TAALLA / "virta.png", dpi=200)


if __name__ == "__main__":
    main()
