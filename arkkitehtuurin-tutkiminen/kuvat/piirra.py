"""Piirtää tutoriaalin kuvat.

Käyttö: python3 kuvat/piirra.py KOHDE JÄLKIHAKEMISTO [INTERVALLIT]

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Luvut lasketaan
samoilla funktioilla kuin lukujen testatuissa esimerkeissä
(esimerkit/arkki). JÄLKIHAKEMISTO on 02-kuormat-esimerkin tuottama
hakemisto (esimerkit/build/02-kuormat) ja INTERVALLIT 06-ydin-esimerkin
kirjoittama tiedosto (esimerkit/build/06-ydin/intervallit.txt).
"""

import importlib.util
import sys
from dataclasses import replace
from pathlib import Path
from types import ModuleType

from matplotlib import rcParams
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "esimerkit"))

from arkki.intervalli import kmeans, simpoint
from arkki.jalki import (
    etaisyydet,
    hutikayra,
    lue_jalki,
    lue_laskurit,
    rivit,
)
from arkki.jonot import eksponentiaalinen, mg1, mm1, mva, simuloi
from arkki.mallit import dynaaminen, epasymmetrinen, symmetrinen
from arkki.siru import arvioi
from arkki.teho import ENERGIA_PJ, sram_energia
from arkki.tutkimus import Tila, pareto, ruudukko

ESIMERKIT = Path(__file__).resolve().parents[1] / "esimerkit"
PILKKU = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
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


def lataa(tiedosto: str) -> ModuleType:
    """Lataa numerolla alkavan esimerkkiohjelman moduulina."""
    nimi = "esimerkki_" + tiedosto.removesuffix(".py").replace("-", "_")
    spec = importlib.util.spec_from_file_location(nimi, ESIMERKIT / tiedosto)
    assert spec is not None and spec.loader is not None
    moduuli = importlib.util.module_from_spec(spec)
    sys.modules[nimi] = moduuli
    spec.loader.exec_module(moduuli)
    return moduuli


def simulaattorit(polku: Path) -> None:
    """Pyynnön viive ytimien määrän funktiona neljällä mallilla.
    Simulaattorien luvut luetaan esimerkin 05-muisti testatusta
    tulosteesta, MVA lasketaan kuten esimerkissä 05-vertailu."""
    viiveet: dict[str, dict[int, float]] = {}
    rivit_ = (ESIMERKIT / "05-muisti" / "odotettu").read_text("utf-8")
    for rivi in rivit_.splitlines()[1:]:
        malli, ytimia, kvantti, _aika, _kaista, viive, _akt = rivi.split()
        if kvantti == "0":
            viiveet.setdefault(malli, {})[int(ytimia)] = float(viive)
    ytimet = sorted(viiveet["sykli"])
    viiveet["mva"] = {n: 44.0 + mva(n, 144.0, [10.0])[1] for n in ytimet}
    fig = kuva(2.7)
    ax = fig.add_subplot()
    for malli, nimi, vari, tyyli in (
            ("sykli", "syklitarkka (vertailukohta)", TUMMA, "o-"),
            ("varaus", "varausmalli", KOROSTUS, "s--"),
            ("mva", "MVA (luku 4)", "#D98C5F", "^-"),
            ("lt", "löyhästi ajastettu", HARMAA, "v:")):
        ax.plot(ytimet, [viiveet[malli][n] for n in ytimet], tyyli,
                color=vari, markersize=3.5, linewidth=1.2, label=nimi)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xticks(ytimet, [str(n) for n in ytimet])
    ax.set_yticks([50, 100, 200], ["50", "100", "200"])
    ax.set_yticks([], minor=True)
    ax.set(xlabel="ytimiä K", ylabel="pyynnön viive (ns)")
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.savefig(polku)


def simpoint_kuva(polku: Path, intervallit: Path) -> None:
    """CPI intervalleittain, ryhmät väreinä ja valitut edustajat.
    Sama data ja samat funktiot kuin esimerkissä 06-simpoint."""
    jaksot, bbv = [], []
    for rivi in intervallit.read_text("ascii").splitlines():
        j, *lohkot = (int(x) for x in rivi.split())
        jaksot.append(j)
        bbv.append(lohkot)
    cpi = [j / 1000 for j in jaksot]
    tarkka = sum(cpi) / len(cpi)
    normitettu = [[x / sum(v) for x in v] for v in bbv]
    ryhmat = kmeans(normitettu, 3, 1)
    _, edustajat = simpoint(bbv, cpi, 3)
    fig = kuva(2.6)
    ax = fig.add_subplot()
    varit = {r: v for r, v in zip(sorted(set(ryhmat)),
                                  (KOROSTUS, TUMMA, "#D98C5F"),
                                  strict=True)}
    ax.bar(range(len(cpi)), cpi, width=1.0,
           color=[varit[r] for r in ryhmat], alpha=0.55)
    for e in edustajat:
        ax.plot([e], [cpi[e]], "v", color=varit[ryhmat[e]], markersize=6,
                markeredgecolor="white", markeredgewidth=0.6, zorder=3)
        ax.annotate("edustaja", (e, cpi[e]), (e, cpi[e] + 0.75),
                    ha="center", fontsize=7)
    ax.axhline(tarkka, color=HARMAA, linestyle="--", linewidth=1)
    ax.text(47, tarkka + 0.1, f"koko ajon CPI {tarkka:.2f}"
            .replace(".", ","), ha="center", fontsize=7.5, color=HARMAA)
    ax.axvspan(-0.5, 4.5, facecolor="none", edgecolor=HARMAA, hatch="///",
               linewidth=0)
    ax.text(5.2, max(cpi) * 1.06, "ajon alku", ha="left", fontsize=7,
            color=HARMAA)
    ax.set(xlabel="intervalli (1000 käskyä)", ylabel="CPI",
           xlim=(-0.5, len(cpi) - 0.5), ylim=(0, max(cpi) * 1.15))
    fig.savefig(polku)


def tasapiste(polku: Path) -> None:
    """Kutsun kesto koon funktiona: ohjelmisto ja kiihdytin."""
    jako = lataa("07-jako.py")
    malli = jako.Jako()
    kysely = replace(malli, keskeytys=200.0)
    koot = [2**i for i in range(13)]
    fig = kuva(2.7)
    ax = fig.add_subplot()
    ax.plot(koot, [malli.ohjelmisto(n) / 1000 for n in koot], color=TUMMA,
            linewidth=1.4, label="ohjelmisto")
    ax.plot(koot, [malli.laitteisto(n) / 1000 for n in koot],
            color=KOROSTUS, linewidth=1.4, label="kiihdytin, keskeytys")
    ax.plot(koot, [kysely.laitteisto(n) / 1000 for n in koot], "--",
            color=KOROSTUS, linewidth=1.2, label="kiihdytin, kysely")
    for m in (malli, kysely):
        n = m.tasapiste()
        ax.plot([n], [m.ohjelmisto(n) / 1000], "o", color=TUMMA,
                markersize=4, zorder=3)
        ax.annotate(f"n = {n}", (n, m.ohjelmisto(n) / 1000),
                    (n * 1.25, m.ohjelmisto(n) / 1000 * 0.52), fontsize=7.5)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set(xlabel="näytteitä kutsussa n", ylabel="kutsun kesto (µs)")
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.savefig(polku)


def dvfs(polku: Path) -> None:
    """Energia jännitteen funktiona: koko tehtävä ja määräaikatehtävä
    alustan tehon kanssa (samat laskut kuin esimerkissä 08-dvfs)."""
    d = lataa("08-dvfs.py")
    ydin, jaksot = d.YDIN, d.JAKSOT
    jannitteet = [0.6 + 0.02 * i for i in range(26)]
    fig = kuva(2.6)
    vasen, oikea = fig.subplots(1, 2)
    energia, viive = [], []
    for v in jannitteet:
        f = ydin.taajuus(v)
        aika = jaksot / (f * 1e9)
        energia.append((ydin.dynaaminen(v, f) + ydin.vuoto(v)) * aika)
        viive.append(aika)
    vasen.plot(jannitteet, energia, color=KOROSTUS, linewidth=1.4,
               label="energia (J)")
    vasen.plot(jannitteet, [e * t for e, t in zip(energia, viive,
                                                  strict=True)],
               color=TUMMA, linewidth=1.4, label="EDP (Js)")
    vasen.set(xlabel="jännite (V)", title="3 Gjaksoa")
    vasen.legend(frameon=False, fontsize=8)
    for alusta, vari in ((0.0, HARMAA), (20.0, KOROSTUS)):
        xs, ys = [], []
        for v in jannitteet:
            f = ydin.taajuus(v)
            aika = jaksot / 2 / (f * 1e9)
            if aika <= 1.0:
                xs.append(v)
                ys.append((ydin.dynaaminen(v, f) + ydin.vuoto(v) + alusta)
                          * aika)
        oikea.plot(xs, ys, color=vari, linewidth=1.4,
                   label=f"alusta {alusta:.0f} W")
        i = min(range(len(ys)), key=ys.__getitem__)
        oikea.plot([xs[i]], [ys[i]], "o", color=vari, markersize=4)
    oikea.set(xlabel="jännite (V)", title="1,5 Gjaksoa, määräaika 1 s",
              ylim=(0, 22))
    oikea.legend(frameon=False, fontsize=8, loc="lower right")
    for ax in (vasen, oikea):
        ax.grid(alpha=0.3)
        ax.title.set_fontsize(8.5)
        ax.xaxis.set_major_formatter(PILKKU)
        ax.yaxis.set_major_formatter(PILKKU)
    fig.savefig(polku)


def valimuisti(polku: Path) -> None:
    """AMAT ja energia viittausta kohden välimuistin koon funktiona."""
    w = lataa("08-valimuisti.py")
    koot = [8 * 2 ** (i / 2) for i in range(21)]
    amat = [w.osumaviive(k) + w.huti(k) * w.DRAM_NS for k in koot]
    energia = [sram_energia(k) + w.huti(k) * 8 * ENERGIA_PJ["DRAM"]
               for k in koot]
    fig = kuva(2.6)
    vasen, oikea = fig.subplots(1, 2)
    for ax, y, nimi in ((vasen, amat, "AMAT (ns)"),
                        (oikea, energia, "energia (pJ/viittaus)")):
        ax.plot(koot, y, color=KOROSTUS, linewidth=1.4)
        i = min(range(len(y)), key=y.__getitem__)
        ax.plot([koot[i]], [y[i]], "o", color=TUMMA, markersize=4)
        paikka = (f"{koot[i]:.0f} KiB" if koot[i] < 1024 else
                  f"noin {koot[i] / 1024:.1f} MiB".replace(".", ","))
        ax.annotate(f"minimi {paikka}", (koot[i], y[i]),
                    (koot[i], y[i] + 0.12 * (max(y) - min(y))),
                    ha="center", fontsize=7.5)
        ax.set_xscale("log", base=2)
        ax.set_xticks([8, 32, 128, 512, 2048, 8192],
                      ["8", "32", "128", "512", "2048", "8192"])
        ax.set(xlabel="välimuistin koko (KiB)", ylabel=nimi, ylim=(0, None))
        ax.yaxis.set_major_formatter(PILKKU)
        ax.grid(alpha=0.3)
    fig.savefig(polku)


def main(argv: list[str]) -> int:
    kohde, jaljet = Path(argv[0]), Path(argv[1])
    simulaattorit(kohde / "simulaattorit.png")
    if len(argv) > 2:
        simpoint_kuva(kohde / "simpoint.png", Path(argv[2]))
    tasapiste(kohde / "tasapiste.png")
    dvfs(kohde / "dvfs.png")
    valimuisti(kohde / "valimuisti.png")
    hutikayrat(kohde / "hutikayra.png", jaljet)
    hill_marty(kohde / "hill-marty.png")
    roofline(kohde / "roofline.png", jaljet)
    jonot(kohde / "jonot.png")
    pareto_kuva(kohde / "pareto.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
