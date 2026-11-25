"""Piirtää tutoriaalin kuvaajat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvaajat piirretään samoista tulostiedostoista, jotka kirjassa näytetään
tulosteina (esimerkit/tulokset/ ja esimerkit/*.odotettu). Kun mittaukset
ajetaan uudelleen (make -C esimerkit tulokset), kuvat päivitetään
komennolla make kuvat. Kuvat commitoidaan, joten tätä ei ajeta
testeissä.
"""

import re
import sys
from pathlib import Path

from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
TULOKSET = ESIMERKIT / "tulokset"

KOROSTUS = "#5B7A14"
TOINEN = "#B07A2A"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 8
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}


def laskurit(tiedosto: str, yksikko: str) -> dict[str, float]:
    """Rivit muotoa "  nimi   12.3 Ir" annetulle yksikölle."""
    tulos: dict[str, float] = {}
    for rivi in (TULOKSET / tiedosto).read_text().splitlines():
        m = re.fullmatch(rf"\s+(\S+)\s+([\d.]+) {yksikko}", rivi)
        if m:
            tulos[m[1]] = float(m[2])
    if not tulos:
        raise SystemExit(f"{tiedosto}: ei yhtään {yksikko}-riviä")
    return tulos


def ajat(tiedosto: str) -> dict[str, tuple[float, float]]:
    """Rivit muotoa "  nimi   1.23 ms +- 0.04": mediaani ja hajonta."""
    tulos: dict[str, tuple[float, float]] = {}
    for rivi in (TULOKSET / tiedosto).read_text().splitlines():
        m = re.match(r"\s+(\S+)\s+([\d.]+) ms \+-\s*([\d.]+)", rivi)
        if m:
            tulos[m[1]] = (float(m[2]), float(m[3]))
    if not tulos:
        raise SystemExit(f"{tiedosto}: ei yhtään aikariviä")
    return tulos


def uusi(leveys: float, korkeus: float) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


def pilkku(teksti: str) -> str:
    """Suomalainen desimaalipilkku."""
    return teksti.replace(".", ",")


PILKKUAKSELI = FuncFormatter(lambda v, _: pilkku(f"{v:g}"))


def pylvaat(ax: Axes, arvot: dict[str, float], otsikko: str, *,
            vari: str = KOROSTUS, virheet: list[float] | None = None,
            log: bool = False, muoto: str = "{:g}") -> None:
    nimet = list(arvot)
    y = list(arvot.values())
    ax.bar(nimet, y, color=vari, width=0.62, yerr=virheet,
           error_kw={"elinewidth": 0.8, "capsize": 2, "ecolor": HARMAA})
    if log:
        ax.set_yscale("log")
    for i, v in enumerate(y):
        lisa = (virheet[i] if virheet else 0)
        ax.annotate(pilkku(muoto.format(v)), (i, v + lisa), (0, 2),
                    textcoords="offset points", ha="center", fontsize=6.5,
                    color=HARMAA)
    else:
        ax.yaxis.set_major_formatter(PILKKUAKSELI)
    ax.set_title(otsikko, fontsize=8, loc="left")
    ax.tick_params(axis="x", labelsize=7, rotation=20)
    ax.margins(y=0.15)


def aikapylvaat(ax: Axes, tiedosto: str, nimet: list[str],
                otsikko: str) -> None:
    a = ajat(tiedosto)
    pylvaat(ax, {n: a[n][0] for n in nimet}, otsikko, vari=TOINEN,
            virheet=[a[n][1] for n in nimet], muoto="{:.3g}")


def kuviot(polku: Path) -> None:
    """Luku 3: käskyt ja aika eivät kerro samaa."""
    nimet = ["virtuaali", "variant", "avoin", "final", "crtp"]
    ir = laskurit("tarkista-kuviot.txt", "Ir")
    fig = uusi(5.6, 2.3)
    vasen, oikea = fig.subplots(1, 2)
    pylvaat(vasen, {n: ir[n] for n in nimet}, "käskyjä kuviota kohden")
    aikapylvaat(oikea, "03-kuviot.txt", nimet, "aika, miljoona kuviota (ms)")
    fig.savefig(polku, metadata=METATIEDOT)


def poikkeukset(polku: Path) -> None:
    """Luku 5: onnistuva ja epäonnistuva polku logaritmisella asteikolla."""
    ir = laskurit("tarkista-poikkeukset.txt", "Ir")
    fig = uusi(4.2, 2.4)
    ax = fig.add_subplot()
    varit = [KOROSTUS, VAALEA, KOROSTUS, VAALEA]
    ax.bar(list(ir), list(ir.values()), color=varit, width=0.62)
    for i, v in enumerate(ir.values()):
        ax.annotate(f"{v:,.0f}".replace(",", " "), (i, v), (0, 2),
                    textcoords="offset points", ha="center", fontsize=6.5,
                    color=HARMAA)
    ax.set_yscale("log")
    ax.set_ylim(50, 60000)
    ax.set_title("käskyjä jäsennystä kohden (logaritminen asteikko)",
                 fontsize=8, loc="left")
    ax.tick_params(axis="x", labelsize=7)
    fig.savefig(polku, metadata=METATIEDOT)


def soa(polku: Path) -> None:
    """Luku 8: SoA tekee enemmän käskyjä mutta vähemmän huteja."""
    nimet = ["aos", "soa"]
    fig = uusi(5.6, 2.1)
    a, b, c = fig.subplots(1, 3)
    ir = laskurit("tarkista-soa.txt", "Ir")
    hudit = laskurit("tarkista-soa.txt", "D1mr")
    pylvaat(a, {n: ir[n] for n in nimet}, "käskyjä / hiukkanen")
    pylvaat(b, {n: hudit[n] for n in nimet}, "L1-huteja / hiukkanen",
            vari=HARMAA)
    aikapylvaat(c, "08-soa.txt", nimet, "aika, miljoona (ms)")
    fig.savefig(polku, metadata=METATIEDOT)


def sailiot(polku: Path) -> None:
    """Luku 8: haun käskyt, hudit ja aika kolmessa säiliössä."""
    nimet = ["map", "litea", "unordered_map"]
    fig = uusi(5.8, 3.6)
    (a, b), (c, d) = fig.subplots(2, 2)
    ir = laskurit("tarkista-sailiot.txt", "Ir")
    l1 = laskurit("tarkista-sailiot.txt", "D1mr")
    ll = laskurit("tarkista-sailiot.txt", "DLmr")
    pylvaat(a, {n: ir[n] for n in nimet}, "käskyjä / haku")
    pylvaat(b, {n: l1[n] for n in nimet}, "L1-huteja / haku", vari=HARMAA)
    pylvaat(c, {n: ll[n] for n in nimet}, "viimeisen tason huteja / haku",
            vari=HARMAA)
    aikapylvaat(d, "08-sailiot.txt", nimet, "aika, 100 000 hakua (ms)")
    for ax in (a, b, c, d):
        ax.tick_params(axis="x", rotation=0)
    fig.savefig(polku, metadata=METATIEDOT)


def muotoilu(polku: Path) -> None:
    """Luku 10: kuusi tapaa muuntaa luku tekstiksi."""
    ir = laskurit("tarkista-muotoilu.txt", "Ir")
    nimet = sorted(ir, key=lambda n: ir[n])
    fig = uusi(4.6, 2.2)
    ax = fig.add_subplot()
    ax.barh(nimet[::-1], [ir[n] for n in nimet[::-1]], color=KOROSTUS,
            height=0.62)
    for i, n in enumerate(nimet[::-1]):
        ax.annotate(f"{ir[n]:.0f}", (ir[n], i), (3, 0),
                    textcoords="offset points", va="center", fontsize=6.5,
                    color=HARMAA)
    ax.set_xlabel("käskyjä muunnosta kohden")
    ax.margins(x=0.1)
    fig.savefig(polku, metadata=METATIEDOT)


def sanat(polku: Path) -> None:
    """Luku 11: varaukset, käskyt ja aika vaiheittain."""
    nimet = ["v1", "v2", "v3", "v4"]
    rivi = (ESIMERKIT / "11-sanat.odotettu").read_text().splitlines()[-1]
    varaukset = {n: float(v) for n, v in re.findall(r"(v\d) (\d+)", rivi)}
    if list(varaukset) != nimet:
        raise SystemExit("11-sanat.odotettu: varausrivi ei vastaa vaiheita")
    ir = laskurit("tarkista-sanat.txt", "Ir")
    fig = uusi(5.8, 2.2)
    a, b, c = fig.subplots(1, 3)
    pylvaat(a, varaukset, "varauksia (20 000 sanaa)", vari=HARMAA)
    pylvaat(b, {n: ir[n] for n in nimet}, "käskyjä / sana", muoto="{:.0f}")
    aikapylvaat(c, "11-sanat.txt", nimet, "aika, miljoona sanaa (ms)")
    for ax in (a, b, c):
        ax.tick_params(axis="x", rotation=0)
    fig.savefig(polku, metadata=METATIEDOT)


def main() -> None:
    kohde = Path(sys.argv[1])
    kohde.mkdir(parents=True, exist_ok=True)
    for nimi, piirra in (("kuviot", kuviot), ("poikkeukset", poikkeukset),
                         ("soa", soa), ("sailiot", sailiot),
                         ("muotoilu", muotoilu), ("sanat", sanat)):
        piirra(kohde / f"{nimi}.png")
        print(f"kuvat/{nimi}.png")


if __name__ == "__main__":
    main()
