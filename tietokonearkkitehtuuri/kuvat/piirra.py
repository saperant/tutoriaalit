"""Piirtää tutoriaalin kuvaajat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Luvut luetaan
esimerkkien .odotettu-tiedostoista, joita testit vertaavat simulaattorin
tulosteeseen: kuvaajat näyttävät siis samat luvut kuin tekstin taulukot.
"""

import sys
from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"

KOROSTUS = "#6D4FA0"
VARIT = ["#B8C4C8", "#8A9AA0", "#5B6B70", "#B07A2A", "#1F2A2E", KOROSTUS]
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}


def rivit(nimi: str) -> list[str]:
    return (ESIMERKIT / nimi).read_text("utf-8").splitlines()


def uusi(leveys: float = 5.4, korkeus: float = 2.8) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


def ennustimet(polku: Path) -> None:
    """Ennustimien tarkkuus ohjelmittain (05-ennustimet.odotettu)."""
    r = rivit("05-ennustimet.odotettu")
    ohjelmat = r[0].split()[2:]
    sarjat = []
    for rivi in r[1:7]:
        nimi, luvut = rivi[:20].strip(), [float(x) for x in rivi[20:].split()]
        assert len(luvut) == len(ohjelmat), rivi
        sarjat.append((nimi, luvut))
    fig = uusi()
    ax = fig.add_subplot()
    leveys = 0.13
    for i, (nimi, luvut) in enumerate(sarjat):
        x = [j + (i - 2.5) * leveys for j in range(len(ohjelmat))]
        ax.bar(x, luvut, leveys, label=nimi, color=VARIT[i])
    ax.set_xticks(range(len(ohjelmat)), ohjelmat)
    ax.set_ylabel("oikein ennustettu (%)")
    ax.set_ylim(0, 100)
    ax.axhline(50, color="#1F2A2E", linewidth=0.6, linestyle=":")
    ax.legend(fontsize=7, ncols=3, loc="lower center",
              bbox_to_anchor=(0.5, 1.0), frameon=False)
    fig.savefig(polku / "ennustimet.png", metadata=METATIEDOT)


def osumasuhde(polku: Path) -> None:
    """Osumasuhde lohkokoon funktiona (06-rakenne.odotettu)."""
    r = rivit("06-rakenne.odotettu")
    alku = next(i for i, x in enumerate(r) if x.lstrip().startswith("koko"))
    lohkot = [int(x) for x in r[alku].split()[1::2]]
    fig = uusi(4.8, 2.8)
    ax = fig.add_subplot()
    sarjat: list[tuple[str, list[float]]] = []
    for rivi in r[alku + 1:]:
        osat = rivi.split()
        luvut = [float(x) for x in osat[2:]]
        assert len(luvut) == len(lohkot), rivi
        if sarjat and sarjat[-1][1] == luvut:     # sama käyrä: yksi selite
            sarjat[-1] = (f"{sarjat[-1][0]} ja {osat[0]} B", luvut)
        else:
            sarjat.append((f"{osat[0]} B", luvut))
    for i, (nimi, luvut) in enumerate(sarjat):
        ax.plot(lohkot, luvut, marker="o", markersize=3.5,
                color=VARIT[i + 1], label=nimi)
    ax.set_xscale("log", base=2)
    ax.set_xticks(lohkot, [str(x) for x in lohkot])
    ax.set_xlabel("lohkon koko (tavua)")
    ax.set_ylabel("osumasuhde (%)")
    ax.set_ylim(0, 100)
    ax.legend(title="välimuistin koko", fontsize=7, title_fontsize=7,
              frameon=False, loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig.savefig(polku / "osumasuhde.png", metadata=METATIEDOT)


def ipc(polku: Path) -> None:
    """IPC ydinkokoonpanon funktiona (11-ilp.odotettu)."""
    r = rivit("11-ilp.odotettu")
    ohjelmat = r[0].split()[1:]
    taulu = {x[:20].strip(): [float(y) for y in x[20:].split()]
             for x in r[1:]}
    jarjestys = ["1-leveä, järj.", "2-leveä, järj.", "4-leveä, järj.",
                 "4-leveä, ikk. 16", "4-leveä, ikk. 128",
                 "8-leveä, ikk. 512"]
    nimet = ["1\njärj.", "2\njärj.", "4\njärj.", "4\nikk. 16",
             "4\nikk. 128", "8\nikk. 512"]
    fig = uusi()
    ax = fig.add_subplot()
    for i, ohjelma in enumerate(ohjelmat):
        ax.plot(range(len(jarjestys)), [taulu[k][i] for k in jarjestys],
                marker="o", markersize=3.5, color=VARIT[i + 1],
                label=ohjelma)
    # Sama 4-leveä ydin 128 käskyn ikkunalla ilman uudelleennimeämistä
    # ja kaksibittisellä ennustimella: vaihteluväli ohjelmien yli.
    for avain, merkki, selite in (
            ("ei uudelleennim.", "v", "ei uudelleennimeämistä"),
            ("2-bit. ennustin", "x", "2-bittinen ennustin")):
        ax.scatter([4] * len(ohjelmat), taulu[avain], marker=merkki, s=18,
                   color="#B4532A", zorder=3, label=selite)
    ax.set_xticks(range(len(jarjestys)), nimet)
    ax.set_xlabel("leveys (käskyä jaksossa) ja ikkuna")
    ax.set_ylabel("IPC")
    ax.set_ylim(0, 8.5)
    ax.legend(fontsize=7, frameon=False, loc="upper left", ncols=2)
    fig.savefig(polku / "ipc.png", metadata=METATIEDOT)


def main() -> None:
    kohde = Path(sys.argv[1] if len(sys.argv) > 1 else "kuvat")
    kohde.mkdir(parents=True, exist_ok=True)
    for piirra in (ennustimet, osumasuhde, ipc):
        piirra(kohde)
        print(f"piirretty: {piirra.__name__}")


if __name__ == "__main__":
    main()
