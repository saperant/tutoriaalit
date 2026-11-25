"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Luvut luetaan
esimerkin testatusta tulosteesta (esimerkit/02-paketti/odotettu).
"""

import re
import sys
from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure

JUURI = Path(__file__).resolve().parent.parent
KOROSTUS = "#A14B7C"
HARMAA = "#5B6B70"
VAALEA = "#EEF1F6"
OTSAKE = 0x50  # päivityspaketin otsakkeen koko (luku 2)
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False


def osa(teksti: str, nimi: str) -> list[str]:
    alku = teksti.index(f"# @alku {nimi}\n") + len(f"# @alku {nimi}\n")
    return teksti[alku:teksti.index(f"# @loppu {nimi}")].splitlines()


def entropia(polku: Path) -> None:
    """Päivityspaketin entropia lohkoittain ja osioiden rajat."""
    teksti = (JUURI / "esimerkit/02-paketti/odotettu").read_text("utf-8")
    pisteet = [(int(m.group(1), 16), float(m.group(2)))
               for rivi in osa(teksti, "s2")
               if (m := re.match(r"([0-9a-f]{6}) (\d\.\d\d)", rivi))]
    # Osioiden pituudet purun tulosteesta: "nimi osoite N tavua raaka".
    osiot = [("otsake", OTSAKE)]
    for rivi in osa(teksti, "s5"):
        if m := re.match(r"\s+(\w+)\s+\S+\s+(\d+) tavua (raaka|zlib)", rivi):
            osiot.append((m.group(1), int(m.group(2))))
    lohko = pisteet[1][0] - pisteet[0][0]
    loppu = sum(koko for _, koko in osiot)

    fig = Figure(figsize=(6.0, 2.8), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    x = [a for a, _ in pisteet] + [loppu]
    y = [e for _, e in pisteet]
    ax.stairs(y, x, color=KOROSTUS, linewidth=1.4, baseline=None)
    kohta = 0
    for n, (nimi, koko) in enumerate(osiot):
        if n % 2 == 0:
            ax.axvspan(kohta, kohta + koko, color=VAALEA, zorder=0)
        if n:
            ax.axvline(kohta, color=HARMAA, linewidth=0.6, linestyle=":")
        ax.text(kohta + koko / 2, 8.25, nimi, ha="center", fontsize=8,
                color=HARMAA)
        kohta += koko
    for raja, selite in ((5.0, "teksti 4–5"), (6.5, "konekieli 5–6,5")):
        ax.axhline(raja, color=HARMAA, linewidth=0.5, linestyle="--")
        ax.text(loppu * 1.01, raja, selite, va="center", fontsize=7,
                color=HARMAA)
    ax.text(loppu * 1.01, 7.7, "pakattu tai\nsalattu > 7,2", va="center",
            fontsize=7, color=HARMAA)
    ax.set_xlim(0, loppu)
    ax.set_ylim(0, 8)
    ax.set_xticks(range(0, loppu, 0x400),
                  [f"0x{a:04x}" for a in range(0, loppu, 0x400)])
    ax.set_xlabel(f"siirtymä tiedostossa ({lohko} tavun lohkot)")
    ax.set_ylabel("entropia (bittiä/tavu)")
    fig.savefig(polku)


def main() -> None:
    kohde = Path(sys.argv[1])
    kohde.mkdir(parents=True, exist_ok=True)
    entropia(kohde / "entropia.png")


if __name__ == "__main__":
    main()
