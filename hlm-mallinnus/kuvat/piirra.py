"""Piirtää tutoriaalin kuvat.

Käyttö: python3 kuvat/piirra.py KOHDE KVANTTIOHJELMA

Kuvat commitoidaan, joten tätä ei ajeta testeissä. KVANTTIOHJELMA on
esimerkin 11-kvantti käännetty ohjelma (esimerkit/build/11-kvantti/
ohjelma). Se ajetaan jälki päällä (toinen argumentti), jolloin se
tulostaa jokaisen siirron simulaatioajan ja aloittajan oman ajan.
"""

import os
import subprocess
import sys
from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure

KOROSTUS = "#B04848"          # alueen Laitteistosuunnittelu väri
TOINEN = "#2F6F8F"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
MUSTE = "#1F2A2E"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
rcParams["text.color"] = MUSTE
rcParams["axes.edgecolor"] = HARMAA
rcParams["axes.labelcolor"] = MUSTE
rcParams["xtick.color"] = HARMAA
rcParams["ytick.color"] = HARMAA

Jalki = dict[str, list[tuple[str, float, float]]]


def aja(ohjelma: Path, kvantti_ns: int) -> Jalki:
    """Ajaa esimerkin jälki päällä ja lukee rivit "J kuka mitä sim oma"."""
    ymparisto = {**os.environ, "SC_COPYRIGHT_MESSAGE": "DISABLE"}
    tuloste = subprocess.run([str(ohjelma), str(kvantti_ns), "jalki"],
                             check=True, capture_output=True, text=True,
                             env=ymparisto).stdout
    jalki: Jalki = {"tuottaja": [], "kuluttaja": []}
    for rivi in tuloste.splitlines():
        if rivi.startswith("J "):
            _, kuka, mita, sim, oma = rivi.split()
            jalki[kuka].append((mita, float(sim), float(oma)))
    return jalki


def kvantti(polku: Path, ohjelma: Path) -> None:
    """Aloittajan oma aika simulaatioajan funktiona kolmella kvantilla.
    Lävistäjällä aloittaja on synkronissa; sen yläpuolella se on edellä."""
    fig = Figure(figsize=(6.4, 2.55), dpi=200, layout="constrained")
    akselit = fig.subplots(1, 3, sharex=True, sharey=True)
    raja = 2400.0
    for ax, (ns, nimi) in zip(akselit, ((0, "kvantti 0"),
                                        (100, "kvantti 100 ns"),
                                        (1000, "kvantti 1 µs")),
                              strict=True):
        jalki = aja(ohjelma, ns)
        ax.plot([0, raja], [0, raja], color=VAALEA, linewidth=0.8)
        for kuka, vari, merkki in (("kuluttaja", TOINEN, "."),
                                   ("tuottaja", KOROSTUS, "o")):
            t = [(s, o) for _, s, o in jalki[kuka] if o <= raja]
            # Aloittaja kulkee ensin omassa ajassaan (pysty) ja siirtää
            # synkronoidessaan simulaatioajan sen tasalle (vaaka).
            ax.plot([s for s, _ in t], [o for _, o in t], "-", color=vari,
                    linewidth=0.7, alpha=0.6, drawstyle="steps-pre")
            ax.plot([s for s, _ in t], [o for _, o in t], merkki,
                    color=vari, markersize=3.2 if merkki == "o" else 2.5,
                    label=kuka)
        uudet = [(s, o) for m, s, o in jalki["kuluttaja"]
                 if m == "uusi" and o <= raja]
        ax.plot([s for s, _ in uudet], [o for _, o in uudet], "v",
                color=MUSTE, markersize=4, label="kuluttaja näkee uuden")
        ax.set_title(nimi, fontsize=8.5)
        ax.set_xlabel("simulaatioaika (ns)")
        ax.set_xlim(0, raja)
        ax.set_ylim(0, raja)
        ax.set_aspect("equal")
        ax.grid(alpha=0.3)
        ax.set_xticks([0, 1000, 2000])
        ax.set_yticks([0, 1000, 2000])
    akselit[0].set_ylabel("aloittajan oma aika (ns)")
    akselit[2].annotate("viesti 4 näkyy\nhetkellä 50 ns,\nlähetetty 830 ns",
                        (0, 50), (420, 330), fontsize=6.5,
                        arrowprops={"arrowstyle": "-", "color": HARMAA,
                                    "linewidth": 0.6})
    akselit[0].legend(frameon=False, fontsize=6.5, loc="lower right",
                      handletextpad=0.3)
    fig.savefig(polku, metadata={"Software": None})


def main() -> None:
    kohde, ohjelma = Path(sys.argv[1]), Path(sys.argv[2])
    kvantti(kohde / "kvantti.png", ohjelma)
    print("kvantti.png")


if __name__ == "__main__":
    main()
