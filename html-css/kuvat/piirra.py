"""Piirtää ajoitusfunktioiden käyrät. Käyttö: python3 kuvat/piirra.py

Kuva commitoidaan, joten tätä ei ajeta testeissä. Käyrät lasketaan
CSS:n määritelmästä: ajoitusfunktio cubic-bezier(x1, y1, x2, y2) on
Bézier-käyrä pisteestä (0, 0) pisteeseen (1, 1).
"""

from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure

HAKEMISTO = Path(__file__).resolve().parent
KOROSTUS = "#1D4F91"
HARMAA = "#5B6B70"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9

# CSS Easing Functions Level 1: avainsanojen ohjauspisteet.
FUNKTIOT = {
    "linear": (0.0, 0.0, 1.0, 1.0),
    "ease": (0.25, 0.1, 0.25, 1.0),
    "ease-in": (0.42, 0.0, 1.0, 1.0),
    "ease-out": (0.0, 0.0, 0.58, 1.0),
    "ease-in-out": (0.42, 0.0, 0.58, 1.0),
}


def bezier(p1: float, p2: float, t: float) -> float:
    """Kuutiollisen Bézier-käyrän koordinaatti, kun päät ovat 0 ja 1."""
    u = 1.0 - t
    return 3 * u * u * t * p1 + 3 * u * t * t * p2 + t ** 3


def kayra(x1: float, y1: float, x2: float, y2: float,
          n: int = 200) -> tuple[list[float], list[float]]:
    ajat = [bezier(x1, x2, i / n) for i in range(n + 1)]
    edistymat = [bezier(y1, y2, i / n) for i in range(n + 1)]
    return ajat, edistymat


def main() -> None:
    fig = Figure(figsize=(6.4, 1.7), dpi=200, layout="constrained")
    akselit = fig.subplots(1, len(FUNKTIOT), sharey=True)
    for ax, (nimi, pisteet) in zip(akselit, FUNKTIOT.items()):
        ajat, edistymat = kayra(*pisteet)
        ax.plot([0, 1], [0, 1], color="#C4C9D2", linewidth=0.8)
        ax.plot(ajat, edistymat, linewidth=1.8,
                color=KOROSTUS if nimi == "ease-out" else HARMAA)
        ax.set_title(nimi, fontsize=9, family="DejaVu Sans Mono")
        ax.set_aspect("equal")
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xlabel("aika", labelpad=-8)
        for reuna in ("top", "right"):
            ax.spines[reuna].set_visible(False)
    akselit[0].set_ylabel("edistymä", labelpad=-4)
    fig.savefig(HAKEMISTO / "14-ajoitusfunktiot.png")


if __name__ == "__main__":
    main()
