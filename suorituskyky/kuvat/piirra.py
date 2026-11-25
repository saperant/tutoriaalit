"""Piirtää tutoriaalin kuvaajat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Luvut luetaan
tiedostoista esimerkit/tulokset/*.txt (kirjoittajan koneen mittaukset,
samat kuin tekstin tulosteissa) ja esimerkit/*.odotettu (testatut
tulosteet). Kun mittaukset ajetaan uudelleen (make -C esimerkit
tulokset), kuvat piirretään uudelleen komennolla make kuvat.
"""

import re
import sys
from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"

KOROSTUS = "#6D4FA0"
TOINEN = "#B07A2A"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
TUMMA = "#1F2A2E"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}


def rivit(nimi: str) -> list[str]:
    return (ESIMERKIT / nimi).read_text("utf-8").splitlines()


def uusi(leveys: float = 5.0, korkeus: float = 2.9) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


def katto(r: list[str]) -> tuple[float, float, list[tuple[str, float, float]]]:
    """Roofline-tulosteesta huippu, kaista ja ytimet (nimi, F/B, GFLOP/s)."""
    m = re.match(r"huippu ([\d.]+) GFLOP/s, kaista ([\d.]+) GB/s", r[1])
    assert m, r[1]
    ytimet = []
    for rivi in r[3:]:
        osat = rivi.split()
        ytimet.append((osat[0], float(osat[-3]), float(osat[-2])))
    return float(m.group(1)), float(m.group(2)), ytimet


def roofline(polku: Path) -> None:
    """Roofline: esimerkkikone (testattu tuloste) ja mitattu kone."""
    fig = uusi(5.2, 3.1)
    ax = fig.add_subplot()
    xs = [0.02, 200.0]
    for nimi, vari, tyyli, selite in (
            ("03-roofline.odotettu", KOROSTUS, "-", "esimerkkikone"),
            ("tulokset/03-roofline.txt", TOINEN, "--",
             "mitattu kone, yksi ydin, skalaari")):
        huippu, kaista, ytimet = katto(rivit(nimi))
        harjanne = huippu / kaista
        ax.plot([xs[0], harjanne, xs[1]],
                [kaista * xs[0], huippu, huippu], color=vari,
                linestyle=tyyli, linewidth=1.6, label=selite)
        ax.plot([harjanne], [huippu], marker="D", markersize=4, color=vari)
        for ydin, intensiteetti, teho in ytimet:
            if intensiteetti <= 0:
                continue                       # kopio: ei laskentaa
            ax.plot([intensiteetti], [teho], marker="o", markersize=4,
                    color=vari, markerfacecolor="white")
            if tyyli == "-":
                ax.annotate(ydin, (intensiteetti, teho), fontsize=7,
                            xytext=(4, -9), textcoords="offset points")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("laskentaintensiteetti (FLOP/tavu)")
    ax.set_ylabel("suorituskyky (GFLOP/s)")
    ax.text(0.03, 1.1, "muistikatto B · I", fontsize=7, rotation=33,
            color=KOROSTUS)
    ax.text(30, 115, "laskentakatto P", fontsize=7, color=KOROSTUS)
    ax.set_ylim(0.2, 300)
    ax.legend(fontsize=7, frameon=False, loc="lower right")
    fig.savefig(polku / "roofline.png", metadata=METATIEDOT)


def latenssi(polku: Path) -> None:
    """Latauksen viive työjoukon koon funktiona (osoitinjahti)."""
    koot, ajat = [], []
    for rivi in rivit("tulokset/05-latenssi.txt")[2:]:
        osat = rivi.split()
        koot.append(int(osat[0]))
        ajat.append(float(osat[2]))
    fig = uusi()
    ax = fig.add_subplot()
    ax.plot(koot, ajat, marker="o", markersize=4, color=KOROSTUS)
    # Kirjoittajan koneen välimuistit (luku 1): L1d 48 KiB, L2 2 MiB.
    for raja, nimi in ((48, "L1d 48 KiB"), (2048, "L2 2 MiB")):
        ax.axvline(raja, color=HARMAA, linewidth=0.7, linestyle=":")
        ax.text(raja * 1.1, 180, nimi, fontsize=7, color=HARMAA)
    ax.set_xscale("log", base=2)
    ax.set_xticks(koot, [f"{k // 1024} Mi" if k >= 1024 else f"{k} Ki"
                         for k in koot])
    ax.set_xlabel("työjoukon koko (tavua)")
    ax.set_ylabel("ns / lataus")
    ax.set_ylim(0, 220)
    fig.savefig(polku / "latenssi.png", metadata=METATIEDOT)


def askel(polku: Path) -> None:
    """Joka k:nnen alkion päivitys: kierroksen aika askeleen funktiona."""
    ks, ms = [], []
    for rivi in rivit("tulokset/05-askel.txt")[2:]:
        osat = rivi.split()
        ks.append(int(osat[0]))
        ms.append(float(osat[1]))
    fig = uusi()
    ax = fig.add_subplot()
    ax.plot(ks, ms, marker="o", markersize=4, color=KOROSTUS,
            label="mitattu")
    # Vertailu: jos aika riippuisi vain päivitysten määrästä.
    ax.plot(ks, [ms[0] / k for k in ks], color=VAALEA, linestyle="--",
            label="työn määrä (1/k)")
    ax.axvline(16, color=HARMAA, linewidth=0.7, linestyle=":")
    ax.text(17.5, 60, "16 alkiota = 64 tavun rivi", fontsize=7,
            color=HARMAA)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xticks(ks, [str(k) for k in ks])
    ax.set_xlabel("askel k (joka k:s alkio päivitetään)")
    ax.set_ylabel("ms / kierros")
    ax.legend(fontsize=7, frameon=False, loc="lower left")
    fig.savefig(polku / "askel.png", metadata=METATIEDOT)


def sumennus(polku: Path) -> None:
    """Tapaustutkimuksen vaiheet: aika, käskyt ja L1-hudit."""
    ajat = [float(r.split()[2]) for r in rivit("tulokset/11-sumennus.txt")
            if r.strip().startswith("vaihe")]
    kaskyt, hudit = [], []
    for rivi in rivit("tulokset/tarkista-sumennus.txt"):
        osat = rivi.split()
        if osat and osat[0].startswith("sumenna_v"):
            kaskyt.append(int(osat[1].replace(",", "")))
            hudit.append(int(osat[3].replace(",", "")))
    assert len(ajat) == len(kaskyt) == 4, (ajat, kaskyt)
    fig = uusi(5.4, 2.6)
    sarjat: tuple[tuple[str, list[float], str], ...] = (
        ("aika, 2048 × 2048 (ms)", ajat, KOROSTUS),
        ("käskyt, 256 × 256 (Ir)", [float(x) for x in kaskyt], HARMAA),
        ("L1-hudit, 256 × 256 (D1mr)", [float(x) for x in hudit], TOINEN))
    for i, (otsikko, arvot, vari) in enumerate(sarjat):
        ax = fig.add_subplot(1, 3, i + 1)
        ax.bar(range(1, 5), arvot, color=vari, width=0.65)
        ax.set_yscale("log")
        ax.set_title(otsikko, fontsize=8)
        ax.set_xticks(range(1, 5))
        ax.set_xlabel("vaihe")
    fig.savefig(polku / "sumennus.png", metadata=METATIEDOT)


def main() -> None:
    kohde = Path(sys.argv[1] if len(sys.argv) > 1 else "kuvat")
    kohde.mkdir(parents=True, exist_ok=True)
    for piirra in (roofline, latenssi, askel, sumennus):
        piirra(kohde)
        print(f"piirretty: {piirra.__name__}")


if __name__ == "__main__":
    main()
