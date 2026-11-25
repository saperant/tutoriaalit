"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat ovat versionhallinnassa, joten tätä ei ajeta testeissä. Kuvat
lasketaan samoilla kaavoilla ja vakioilla kuin esimerkit 10-amdahl.cpp
ja 10-tyonjako.cpp, ja skripti tarkistaa tuloksensa esimerkkien
testatuista tulosteista (esimerkit/*.odotettu).
"""

import sys
from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure

JUURI = Path(__file__).resolve().parent.parent
KOROSTUS = "#B04848"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False


def amdahl(s: float, p: float) -> float:
    return 1.0 / (s + (1.0 - s) / p)


def gustafson(s: float, p: float) -> float:
    return s + (1.0 - s) * p


def nopeutus(polku: Path) -> None:
    """Amdahlin ja Gustafsonin lait (taulukko: 10-amdahl.odotettu)."""
    rivit = (JUURI / "esimerkit/10-amdahl.odotettu").read_text(
        "utf-8").splitlines()[1:]
    osuudet = []
    for rivi in rivit:
        osat = rivi.split()
        s = int(osat[0]) / 100
        # Taulukon sarakkeet: p=4, p=16, p=64, raja, Gustafson p=64.
        assert f"{amdahl(s, 64):.2f}" == osat[4], rivi
        assert f"{gustafson(s, 64):.1f}" == osat[6], rivi
        osuudet.append(s)
    ytimet = [2 ** k for k in range(0, 11)]
    fig = Figure(figsize=(6.4, 2.7), dpi=200, layout="constrained")
    vasen, oikea = fig.subplots(1, 2)
    for s in osuudet:
        vari = KOROSTUS if s == 0.05 else HARMAA
        vasen.plot(ytimet, [amdahl(s, p) for p in ytimet], "-o",
                   color=vari, markersize=2.5, linewidth=1.1)
        vasen.annotate(f"s = {s:.0%}".replace("%", " %"),
                       (ytimet[-1], amdahl(s, ytimet[-1])),
                       xytext=(5, 0), textcoords="offset points",
                       va="center", fontsize=8)
        oikea.plot(ytimet, [gustafson(s, p) for p in ytimet], "-o",
                   color=vari, markersize=2.5, linewidth=1.1)
    vasen.plot(ytimet, ytimet, ":", color="#222222", linewidth=0.9)
    oikea.plot(ytimet, ytimet, ":", color="#222222", linewidth=0.9)
    for ax, nimi in ((vasen, "Amdahl: sama ongelma"),
                     (oikea, "Gustafson: ongelma kasvaa")):
        ax.set_xscale("log", base=2)
        ax.set_yscale("log", base=2)
        ax.set_xticks([1, 4, 16, 64, 256, 1024],
                      ["1", "4", "16", "64", "256", "1024"])
        ax.set_yticks([1, 4, 16, 64, 256, 1024],
                      ["1", "4", "16", "64", "256", "1024"])
        ax.set_xlim(0.9, 4096)
        ax.set_ylim(0.9, 1500)
        ax.set_xlabel("suorittimia p")
        ax.set_title(nimi, fontsize=9)
        ax.grid(True, which="major", color=VAALEA, linewidth=0.5)
    vasen.set_ylabel("nopeutus")
    fig.savefig(polku / "nopeutus.png", metadata={"Software": None})


def tyonjako(polku: Path) -> None:
    """Säiekohtainen kuorma kahdella jaolla (10-tyonjako.odotettu)."""
    tehtavia, saikeita = 4000, 4
    staattinen = [sum(i + 1 for i in range(s * tehtavia // saikeita,
                                            (s + 1) * tehtavia // saikeita))
                  for s in range(saikeita)]
    syklinen = [sum(i + 1 for i in range(s, tehtavia, saikeita))
                for s in range(saikeita)]
    odotettu = (JUURI / "esimerkit/10-tyonjako.odotettu").read_text("utf-8")
    keski = sum(staattinen) / saikeita
    for nimi, kuorma in (("staattinen", staattinen), ("syklinen", syklinen)):
        suhde = f"suurin/keskiarvo {max(kuorma) / keski:.2f}"
        assert f"{nimi}: jokainen kerran kylla, {suhde}" in odotettu, nimi
    fig = Figure(figsize=(6.0, 2.3), dpi=200, layout="constrained")
    akselit = fig.subplots(1, 2, sharey=True)
    for ax, nimi, kuorma in ((akselit[0], "staattinen yhtenäinen jako",
                              staattinen),
                             (akselit[1], "syklinen jako", syklinen)):
        suhteet = [k / keski for k in kuorma]
        ax.bar(range(saikeita), suhteet, width=0.6,
               color=[KOROSTUS if k == max(suhteet) and k > 1.01 else HARMAA
                      for k in suhteet])
        ax.axhline(1.0, color="#222222", linewidth=0.8, linestyle=":")
        ax.set_xticks(range(saikeita), [f"säie {s}" for s in range(saikeita)])
        ax.set_title(nimi, fontsize=9)
        for s, k in enumerate(suhteet):
            ax.annotate(f"{k:.2f}".replace(".", ","), (s, k),
                        xytext=(0, 2), textcoords="offset points",
                        ha="center", fontsize=8)
    akselit[0].set_ylabel("kuorma / keskiarvo")
    akselit[0].set_ylim(0, 2.0)
    akselit[0].set_yticks([0, 0.5, 1.0, 1.5, 2.0],
                          ["0", "0,5", "1,0", "1,5", "2,0"])
    fig.savefig(polku / "tyonjako.png", metadata={"Software": None})


def main() -> None:
    kohde = Path(sys.argv[1])
    nopeutus(kohde)
    tyonjako(kohde)


if __name__ == "__main__":
    main()
