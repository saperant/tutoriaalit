"""Piirtää tutoriaalin aikajanakuvat. Käyttö: python3 kuvat/piirra.py

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Ajat ovat samat kuin
esimerkkien testeissä: kilpatilanteen järjestys testistä
esimerkit/src/07-verkko/useHaku.test.tsx ja vesiputouksen kestot
(kolme 100 ms:n pyyntöä) testistä
esimerkit/src/11-suorituskyky/vesiputous.test.ts.
"""

from pathlib import Path

from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.figure import Figure

HAKEMISTO = Path(__file__).resolve().parent
SININEN = "#1D4F91"
VAALEA = "#C7D9F2"
HARMAA = "#5B6472"
PUNAINEN = "#B3261E"
VIHREA = "#2E7D4F"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9


def palkki(ax: Axes, rivi: float, alku: float, loppu: float, teksti: str,
           vari: str = VAALEA, reuna: str = SININEN,
           tekstivari: str = "#1A1F29") -> None:
    ax.barh(rivi, loppu - alku, left=alku, height=0.6, color=vari,
            edgecolor=reuna, linewidth=1)
    ax.text((alku + loppu) / 2, rivi, teksti, ha="center", va="center",
            color=tekstivari, fontsize=8)


def siisti(ax: Axes, rivit: list[str]) -> None:
    ax.set_yticks(range(len(rivit)), rivit)
    ax.set_ylim(len(rivit) - 0.5, -0.5)     # ensimmäinen rivi ylimmäksi
    ax.tick_params(left=False)
    for reuna in ("top", "right", "left"):
        ax.spines[reuna].set_visible(False)


def kilpatilanne() -> None:
    """Aalto pyydetään ensin mutta se vastaa viimeisenä."""
    fig = Figure(figsize=(6.4, 2.0), dpi=200, layout="constrained")
    vasen, oikea = fig.subplots(1, 2, sharey=True)
    rivit = ["pyyntö: Aalto", "pyyntö: Kivi", "näkymä"]
    for ax, peruutus in ((vasen, False), (oikea, True)):
        if peruutus:
            palkki(ax, 0, 0, 1, "peruttu", "#ECEFF3", HARMAA, HARMAA)
            ax.plot([1], [0], marker="x", color=PUNAINEN, markersize=7,
                    markeredgewidth=2)
        else:
            palkki(ax, 0, 0, 3, "hidas vastaus")
        palkki(ax, 1, 1, 2, "vastaus")
        palkki(ax, 2, 0, 2, "Ladataan…", "#ECEFF3", HARMAA)
        if peruutus:
            palkki(ax, 2, 2, 4, "Kivi", "#DDEFE3", VIHREA)
        else:
            palkki(ax, 2, 2, 3, "Kivi", "#DDEFE3", VIHREA)
            palkki(ax, 2, 3, 4, "Aalto", "#FDECEA", PUNAINEN, PUNAINEN)
        ax.axvline(1, color=HARMAA, linewidth=0.8, linestyle=":")
        ax.text(1, -0.5, "käyttäjä valitsee Kiven", ha="center",
                va="bottom", fontsize=7.5, color=HARMAA)
        ax.set_xlim(0, 4)
        ax.set_xticks([])
        ax.set_xlabel("aika →")
        ax.set_title("Peruutuksella" if peruutus else "Ilman peruutusta",
                     fontsize=9, pad=14)
        siisti(ax, rivit)
    fig.savefig(HAKEMISTO / "07-kilpatilanne.png")


def vesiputous() -> None:
    """Kolme 100 ms:n pyyntöä peräkkäin ja rinnakkain."""
    fig = Figure(figsize=(6.4, 1.8), dpi=200, layout="constrained")
    vasen, oikea = fig.subplots(1, 2, sharey=True)
    rivit = ["Aalto", "Kivi", "Tove"]
    for ax, rinnakkain in ((vasen, False), (oikea, True)):
        for i in range(3):
            alku = 0 if rinnakkain else i * 100
            palkki(ax, i, alku, alku + 100, "100 ms")
        valmis = 100 if rinnakkain else 300
        ax.axvline(valmis, color=PUNAINEN if not rinnakkain else VIHREA,
                   linewidth=1.2)
        ax.set_xlim(0, 320)
        ax.set_xticks([0, 100, 200, 300])
        ax.set_xlabel("aika (ms)")
        ax.set_title(
            f"{'Rinnakkain' if rinnakkain else 'Peräkkäin'}: "
            f"valmis {valmis} ms", fontsize=9)
        siisti(ax, rivit)
    fig.savefig(HAKEMISTO / "11-vesiputous.png")


if __name__ == "__main__":
    kilpatilanne()
    vesiputous()
