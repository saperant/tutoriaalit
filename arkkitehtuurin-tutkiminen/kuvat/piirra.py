"""Piirtää tutoriaalin kuvat.

Käyttö: python3 kuvat/piirra.py KOHDE JÄLKIHAKEMISTO

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Luvut lasketaan
samoilla funktioilla kuin lukujen testatuissa esimerkeissä
(esimerkit/arkki). JÄLKIHAKEMISTO on 02-kuormat-esimerkin tuottama
hakemisto (esimerkit/build/02-kuormat).
"""

import sys
from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "esimerkit"))

from arkki.jalki import (etaisyydet, hutikayra,  # noqa: E402
                         lue_jalki, lue_laskurit, rivit)
from arkki.jonot import eksponentiaalinen, mg1, mm1, simuloi  # noqa: E402
from arkki.mallit import (dynaaminen, epasymmetrinen,  # noqa: E402
                          symmetrinen)
from arkki.siru import arvioi  # noqa: E402
from arkki.tutkimus import Tila, pareto, ruudukko  # noqa: E402

KOROSTUS = "#B04848"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
TUMMA = "#1F2A2E"
VARIT = [KOROSTUS, TUMMA, HARMAA, "#D98C5F"]
YTIMET = ["virta", "naiivi", "lohkottu", "lista"]
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False


def kuva(korkeus: float = 2.6) -> Figure:
    return Figure(figsize=(6.4, korkeus), dpi=200, layout="constrained")


def hutikayrat(polku: Path, jaljet: Path) -> None:
    koot_kib = [0.25 * 2**i for i in range(10)]
    fig = kuva()
    ax = fig.add_subplot()
    for ydin, vari in zip(YTIMET, VARIT, strict=True):
        r = rivit(lue_jalki(jaljet / f"{ydin}.txt"))
        koot = [int(k * 16) for k in koot_kib]
        h = hutikayra(etaisyydet(r), koot)
        ax.plot(koot_kib, [100 * h[k] / len(r) for k in koot], "o-",
                color=vari, markersize=3, linewidth=1.4, label=ydin)
    ax.set_xscale("log", base=2)
    ax.set(xlabel="välimuistin koko (KiB), täysin assosiatiivinen LRU",
           ylabel="hudit (%)", ylim=(0, 60))
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, fontsize=8, ncols=4, loc="upper right")
    fig.savefig(polku)


def hill_marty(polku: Path) -> None:
    koot = [1, 2, 4, 8, 16, 32, 64]
    fig = kuva()
    akselit = fig.subplots(1, 2, sharey=True)
    for ax, f in zip(akselit, (0.9, 0.99), strict=True):
        for malli, nimi, vari in ((symmetrinen, "symmetrinen", KOROSTUS),
                                  (epasymmetrinen, "epäsymmetrinen", TUMMA),
                                  (dynaaminen, "dynaaminen", HARMAA)):
            ax.plot(koot, [malli(f, 64, r) for r in koot], "o-",
                    color=vari, markersize=3, linewidth=1.4, label=nimi)
        ax.set_xscale("log", base=2)
        ax.set(title=f"f = {f}", xlabel="ytimen koko r (BCE)")
        ax.grid(alpha=0.3)
    akselit[0].set(ylabel="nopeutus (64 BCE)")
    akselit[0].legend(frameon=False, fontsize=8)
    fig.savefig(polku)


def roofline(polku: Path, jaljet: Path) -> None:
    huippu, kaistat = 32.0, {"L1": 128.0, "L2": 64.0, "muisti": 16.0}
    laskurit = lue_laskurit(jaljet / "laskurit.txt")
    fig = kuva(2.8)
    ax = fig.add_subplot()
    x = [2.0**i for i in range(-7, 5)]
    for (nimi, b), tyyli in zip(kaistat.items(), (":", "--", "-"),
                                strict=True):
        ax.plot(x, [min(huippu, b * i) for i in x], tyyli, color=HARMAA,
                linewidth=1.2, label=f"{nimi} {b:.0f} GB/s")
    for ydin, vari in zip(YTIMET, VARIT, strict=True):
        r = rivit(lue_jalki(jaljet / f"{ydin}.txt"))
        h = hutikayra(etaisyydet(r), [128])
        i = laskurit[ydin].liukuluku / (64 * h[128])
        ax.plot([i], [min(huippu, kaistat["muisti"] * i)], "o", color=vari,
                markersize=6, label=f"{ydin} (muisti)")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=2)
    ax.set(xlabel="intensiteetti (FLOP/B)", ylabel="GFLOP/s")
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, fontsize=7, ncols=2, loc="lower right")
    fig.savefig(polku)


def jonot(polku: Path) -> None:
    s = 10.0
    kuormat = [0.05 * i for i in range(1, 20)]
    fig = kuva()
    ax = fig.add_subplot()
    ax.plot(kuormat, [mm1(r / s, 1 / s).viipyma for r in kuormat],
            color=KOROSTUS, linewidth=1.4, label="M/M/1")
    ax.plot(kuormat, [mg1(r / s, s, s * s).viipyma for r in kuormat],
            color=TUMMA, linewidth=1.4, label="M/D/1")
    sim = [0.3, 0.5, 0.7, 0.8, 0.9]
    ax.plot(sim, [simuloi(r / s, eksponentiaalinen(s), 1, 100_000, 7)
                  .viipyma for r in sim], "o", color=KOROSTUS,
            markersize=4, label="M/M/1 simuloitu")
    ax.set(xlabel="käyttöaste", ylabel="viipymä (ns)", ylim=(0, 200))
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, fontsize=8)
    fig.savefig(polku)


def pareto_kuva(polku: Path) -> None:
    tila: Tila = {"r": [1, 2, 4, 8, 16], "c": [2, 4, 8, 16, 32],
            "v": [0.6, 0.7, 0.8, 0.9, 1.0, 1.1]}
    pisteet = ruudukko(tila)
    tulokset = [arvioi(p["r"], p["c"], p["v"]) for p in pisteet]
    rintama = sorted(pareto([(-t.nopeutus, t.teho) for t in tulokset]),
                     key=lambda i: tulokset[i].teho)
    fig = kuva(2.8)
    ax = fig.add_subplot()
    ax.plot([t.teho for t in tulokset], [t.nopeutus for t in tulokset],
            "o", color=VAALEA, markersize=3, label="kaikki 150 pistettä")
    ax.plot([tulokset[i].teho for i in rintama],
            [tulokset[i].nopeutus for i in rintama], "o-", color=KOROSTUS,
            markersize=4, linewidth=1.2, label="Pareto-rintama")
    ax.axvline(80, color=TUMMA, linestyle="--", linewidth=1,
               label="tehoraja 80 W")
    ax.set(xlabel="teho (W)", ylabel="nopeutus")
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.savefig(polku)


def main(argv: list[str]) -> int:
    kohde, jaljet = Path(argv[0]), Path(argv[1])
    hutikayrat(kohde / "hutikayra.png", jaljet)
    hill_marty(kohde / "hill-marty.png")
    roofline(kohde / "roofline.png", jaljet)
    jonot(kohde / "jonot.png")
    pareto_kuva(kohde / "pareto.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
