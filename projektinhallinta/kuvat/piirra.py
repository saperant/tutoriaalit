"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Luvut lasketaan
samoilla funktioilla kuin lukujen testatuissa esimerkeissä.
"""

import contextlib
import importlib.util
import io
import random
import sys
from pathlib import Path
from types import ModuleType

from matplotlib import rcParams
from matplotlib.figure import Figure

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
sys.path.insert(0, str(ESIMERKIT))

import ennuste  # noqa: E402
import virtaus  # noqa: E402

KOROSTUS = "#1D6F80"
TOINEN = "#B07A2A"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}


def lataa(nimi: str) -> ModuleType:
    """Lataa numeroidun esimerkin moduulina ja vaimentaa sen tulosteen."""
    spec = importlib.util.spec_from_file_location(
        nimi.replace("-", "_"), ESIMERKIT / f"{nimi}.py")
    assert spec is not None and spec.loader is not None
    moduuli = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(moduuli)
    return moduuli


def tallenna(fig: Figure, polku: Path) -> None:
    fig.savefig(polku, metadata=METATIEDOT)


def uusi(leveys: float = 4.4, korkeus: float = 2.7) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


def summa(polku: Path) -> None:
    """Kymmenen tehtävän projektin keston jakauma."""
    m = lataa("01-summa")
    fig = uusi()
    ax = fig.add_subplot()
    ax.hist(m.kestot, bins=60, color=VAALEA)
    for x, nimi, vari in ((m.suunnitelma, "todennäköisimpien\nsumma", TOINEN),
                          (m.persentiili(m.kestot, 0.5), "50 %", HARMAA),
                          (m.persentiili(m.kestot, 0.85), "85 %", KOROSTUS)):
        ax.axvline(x, color=vari, linewidth=1.2)
        ax.text(x + 0.6, ax.get_ylim()[1] * 0.93, nimi, color=vari,
                va="top", fontsize=8)
    ax.set_xlabel("projektin kesto (pv)")
    ax.set_yticks([])
    ax.set_xlim(45, 105)
    tallenna(fig, polku)


def kartio(polku: Path) -> None:
    """Epävarmuuskartio: arvion vaihteluväli projektin vaiheittain."""
    vaiheet = ["idea", "tuote\nmääritelty", "vaatimukset\nvalmiit",
               "käyttöliittymä\nsuunniteltu", "yksityiskohdat\nsuunniteltu",
               "valmis"]
    yla = [4.0, 2.0, 1.5, 1.25, 1.1, 1.0]
    ala = [0.25, 0.5, 0.67, 0.8, 0.9, 1.0]
    fig = uusi(4.8, 2.8)
    ax = fig.add_subplot()
    x = range(len(vaiheet))
    ax.fill_between(x, ala, yla, color=VAALEA, alpha=0.6)
    ax.plot(x, yla, color=KOROSTUS, linewidth=1.2, marker="o", markersize=3)
    ax.plot(x, ala, color=KOROSTUS, linewidth=1.2, marker="o", markersize=3)
    ax.axhline(1.0, color=HARMAA, linewidth=0.6, linestyle=":")
    ax.set_yscale("log", base=2)
    ax.set_yticks([0.25, 0.5, 1, 2, 4], ["0,25×", "0,5×", "1×", "2×", "4×"])
    ax.set_xticks(list(x), vaiheet, fontsize=7)
    ax.set_ylabel("arvio / toteuma")
    tallenna(fig, polku)


def palaute(polku: Path) -> None:
    """Erän koon U-käyrä kahdella palautekierroksen hinnalla."""
    m = lataa("03-palaute")
    erat = [1, 2, 4, 5, 8, 10, 20, 40]
    fig = uusi()
    ax = fig.add_subplot()
    for hinta, vari in ((2.0, KOROSTUS), (0.5, TOINEN)):
        ax.plot(erat, [m.kokonaistyo(e, hinta) for e in erat], color=vari,
                marker="o", markersize=3, linewidth=1.2,
                label=f"palautekierros {str(hinta).replace('.', ',')} pv")
    ax.plot(erat, [200 + m.uudelleentyo(e) for e in erat], color=VAALEA,
            linewidth=1, linestyle="--", label="työ + uudelleentyö")
    ax.set_xscale("log", base=2)
    ax.set_xticks(erat, [str(e) for e in erat])
    ax.set_xlabel("erän koko (ominaisuutta ennen palautetta)")
    ax.set_ylabel("kokonaistyö (pv)")
    ax.legend(frameon=False, fontsize=7)
    tallenna(fig, polku)


def ennustekuva(polku: Path) -> None:
    """Monte Carlo -ennusteen jakauma ja varmuustasot."""
    viikot = ennuste.valmistumisennuste(ennuste.HISTORIA, 60)
    fig = uusi()
    ax = fig.add_subplot()
    arvot = sorted(set(viikot))
    ax.bar(arvot, [viikot.count(v) / len(viikot) for v in arvot],
           color=VAALEA, width=0.85)
    for osuus, vari in ((0.5, HARMAA), (0.85, KOROSTUS), (0.95, TOINEN)):
        x = ennuste.persentiili(viikot, osuus)
        ax.axvline(x + 0.45, color=vari, linewidth=1.2)
        ax.text(x + 0.55, ax.get_ylim()[1] * (0.4 + osuus / 2),
                f"{osuus:.0%}".replace("%", " %"), color=vari, fontsize=8)
    ax.set_xlabel("viikko, jolla 60 työtä on valmiina")
    ax.set_ylabel("osuus toistoista")
    ax.set_xticks(arvot)
    tallenna(fig, polku)


def cfd(polku: Path) -> None:
    """Kumulatiivinen virtauskaavio rajalla ja ilman."""
    fig = uusi(5.4, 2.6)
    for i, (raja, otsikko) in enumerate(((4, "WIP-raja 4"),
                                         (None, "ei rajaa"))):
        ax = fig.add_subplot(1, 2, i + 1)
        k = virtaus.simuloi(raja, 160).kertymat[100:160]
        x = range(100, 160)
        saapuneet = [a for a, _, _ in k]
        aloitetut = [b for _, b, _ in k]
        valmiit = [c for _, _, c in k]
        ax.fill_between(x, aloitetut, saapuneet, color=VAALEA,
                        label="jonossa")
        ax.fill_between(x, valmiit, aloitetut, color=TOINEN, alpha=0.7,
                        label="työn alla")
        ax.fill_between(x, min(valmiit), valmiit, color=KOROSTUS,
                        alpha=0.8, label="valmiit")
        ax.set_title(otsikko, fontsize=9)
        ax.set_xlabel("päivä")
        if i == 0:
            ax.set_ylabel("töitä (kertymä)")
            ax.legend(frameon=False, fontsize=7, loc="upper left")
    tallenna(fig, polku)


def lapimeno(polku: Path) -> None:
    """Läpimenoaikojen hajontakuvio ja persentiilit."""
    tyot = [t for t in virtaus.simuloi(4, 400).valmiit if t.aloitettu >= 100]
    ajat = sorted(t.lapimenoaika for t in tyot)
    fig = uusi()
    ax = fig.add_subplot()
    ax.scatter([t.valmis for t in tyot], [t.lapimenoaika for t in tyot],
               s=5, color=HARMAA, alpha=0.6, linewidths=0)
    for osuus, vari in ((0.5, HARMAA), (0.85, KOROSTUS), (0.95, TOINEN)):
        y = ajat[int(osuus * len(ajat))]
        ax.axhline(y, color=vari, linewidth=1)
        ax.text(402, y, f"{osuus:.0%}: {y:.0f} pv".replace("%", " %"),
                color=vari, fontsize=7, va="center")
    ax.set_xlabel("valmistumispäivä")
    ax.set_ylabel("läpimenoaika (pv)")
    tallenna(fig, polku)


def kuormitus(polku: Path) -> None:
    """Läpimenoaika kuormitusasteen funktiona (M/M/1)."""
    fig = uusi()
    ax = fig.add_subplot()
    x = [i / 200 for i in range(0, 193)]
    ax.plot([100 * v for v in x], [1 / (1 - v) for v in x], color=KOROSTUS,
            linewidth=1.4)
    rng = random.Random(8)
    m = lataa("07-jono")
    pisteet = (0.5, 0.7, 0.8, 0.9, 0.95)
    ax.plot([100 * p for p in pisteet],
            [m.lapimenoaika(p, rng) for p in pisteet], "o", color=TOINEN,
            markersize=4, label="simuloitu")
    ax.set_xlabel("kuormitusaste (%)")
    ax.set_ylabel("läpimenoaika / työn kesto")
    ax.set_ylim(0, 22)
    ax.legend(frameon=False, fontsize=7)
    tallenna(fig, polku)


def velka(polku: Path) -> None:
    """Kertyneet ominaisuudet neljällä velkastrategialla."""
    m = lataa("08-velka")
    fig = uusi(4.8, 2.8)
    ax = fig.add_subplot()
    varit = (HARMAA, TOINEN, VAALEA, KOROSTUS)
    for (nimi, strategia), vari in zip(m.STRATEGIAT.items(), varit,
                                       strict=True):
        kertyma, _ = m.aja(strategia)
        ax.plot(range(1, 41), kertyma, color=vari, linewidth=1.4, label=nimi)
    ax.axvline(8, color=HARMAA, linewidth=0.6, linestyle=":")
    ax.set_xlabel("sprintti")
    ax.set_ylabel("valmiita ominaisuuksia (kertymä)")
    ax.legend(frameon=False, fontsize=7)
    tallenna(fig, polku)


KUVAT = {"summa": summa, "kartio": kartio, "palaute": palaute,
         "ennuste": ennustekuva, "cfd": cfd, "lapimeno": lapimeno,
         "kuormitus": kuormitus, "velka": velka}

if __name__ == "__main__":
    kohde = Path(sys.argv[1])
    kohde.mkdir(parents=True, exist_ok=True)
    for nimi, piirra in KUVAT.items():
        piirra(kohde / f"{nimi}.png")
        print(f"{nimi}.png")
