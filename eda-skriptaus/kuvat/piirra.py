"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Data tulee samasta
kirjastosta ja samoista kuvauksista kuin esimerkkien tulosteet:
historiakuva ajaa luvun 8 esimerkin regressiot uudelleen ja lukee
tulokset historiatietokannasta, ja bittikenttäkuva piirretään
rekisterikuvauksesta asetukset/rekisterit.toml.
"""

import importlib.util
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
sys.path.insert(0, str(ESIMERKIT))

from vuo.historia import avaa, kirjaa, trendi
from vuo.regressio import Testi, aja_regressio
from vuo.rekisterit import lue

KOROSTUS = "#546676"
VIRHE = "#B4532A"
OK = "#6E9A6B"
HARMAA = "#5B6B70"
VAALEA = "#D9E0E3"
TUMMA = "#1F2A2E"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}


def tallenna(fig: Figure, polku: Path) -> None:
    fig.savefig(polku, metadata=METATIEDOT)


def historia(polku: Path) -> None:
    """Läpäisyosuus versioittain ja siemen x versio -ruudukko."""
    spec = importlib.util.spec_from_file_location(
        "historiaesimerkki", ESIMERKIT / "08-historia.py")
    assert spec and spec.loader
    esimerkki = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(esimerkki)
    versiot = esimerkki.VERSIOT

    with tempfile.TemporaryDirectory() as tmp:
        yhteys = avaa(Path(tmp) / "historia.db")
        for jarjestys, (versio, maarittelyt) in enumerate(versiot, 1):
            testi = Testi("alu", tuple(range(1, 9)), maara=12,
                          maarittelyt=maarittelyt)
            tulokset = aja_regressio(ESIMERKIT, Path(tmp) / "ajo", [testi])
            kirjaa(yhteys, versio, jarjestys, tulokset)
        uusinta = [replace(t, tila="ok", viestit=()) if t.siemen == 7
                   else t for t in tulokset]
        kirjaa(yhteys, "c4", len(versiot), uusinta)
        osuudet = trendi(yhteys)
        # Jokainen ajo omana sarakkeenaan, myös uusinta.
        ajot = yhteys.execute(
            "SELECT id, versio FROM ajo ORDER BY jarjestys, id").fetchall()
        ruudut = {(ajo, siemen): tila for ajo, siemen, tila in
                  yhteys.execute("SELECT ajo, siemen, tila FROM tulos")}
        yhteys.close()

    fig = Figure(figsize=(6.2, 2.5), dpi=200, layout="constrained")
    vasen, oikea = fig.subplots(1, 2, width_ratios=(1, 1.25))
    nimet = [v for v, _, _ in osuudet]
    prosentit = [100 * ok / n for _, ok, n in osuudet]
    vasen.plot(nimet, prosentit, color=KOROSTUS, marker="o", linewidth=1.4)
    for x, (p, (_, ok, n)) in enumerate(zip(prosentit, osuudet,
                                            strict=True)):
        vasen.annotate(f"{ok}/{n}", (x, p), textcoords="offset points",
                       xytext=(0, 6), ha="center", fontsize=7.5,
                       color=TUMMA)
    vasen.set(ylim=(0, 115), ylabel="läpäisseitä (%)", xlabel="versio",
              title="Trendi (viimeisin ajo)")
    vasen.title.set_fontsize(9)

    siemenet = sorted({s for _, s in ruudut})
    for x, (ajo, _) in enumerate(ajot):
        for y, siemen in enumerate(siemenet):
            vari = OK if ruudut[(ajo, siemen)] == "ok" else VIRHE
            oikea.add_patch(Rectangle((x + 0.06, y + 0.06), 0.88, 0.88,
                                      color=vari))
    otsikot = [v for _, v in ajot]
    otsikot[-1] += "\n(uusinta)"
    oikea.set(xlim=(0, len(ajot)), ylim=(len(siemenet), 0),
              xticks=[x + 0.5 for x in range(len(ajot))],
              xticklabels=otsikot,
              yticks=[y + 0.5 for y in range(len(siemenet))],
              yticklabels=siemenet, ylabel="siemen",
              title="Jokainen ajo: vihreä läpi, punainen hylätty")
    oikea.title.set_fontsize(9)
    oikea.tick_params(length=0)
    for reuna in oikea.spines.values():
        reuna.set_visible(False)
    tallenna(fig, polku)


def bittikentat(polku: Path) -> None:
    """CTRL- ja STATUS-rekisterin kentät, pääsy ja nollausarvo."""
    lohko = lue(ESIMERKIT / "asetukset" / "rekisterit.toml")
    rekisterit = [r for r in lohko.rekisterit
                  if r.nimi in ("CTRL", "STATUS")]
    bitteja = 16                     # ylemmät 16 bittiä ovat varattuja
    fig = Figure(figsize=(6.2, 1.25 * len(rekisterit) + 0.2), dpi=200,
                 layout="constrained")
    for ax, r in zip(fig.subplots(len(rekisterit), 1), rekisterit,
                     strict=True):
        ax.add_patch(Rectangle((0, 0), bitteja, 1, facecolor=VAALEA,
                               edgecolor=HARMAA, linewidth=0.6))
        selitteet = []
        for k in sorted(r.kentat, key=lambda k: -k.msb):
            vasen = bitteja - 1 - k.msb
            ax.add_patch(Rectangle((vasen, 0), k.leveys, 1,
                                   facecolor="white", edgecolor=TUMMA,
                                   linewidth=0.9))
            kapea = k.leveys < 3
            ax.text(vasen + k.leveys / 2, 0.5, k.nimi, ha="center",
                    va="center", fontsize=6.5 if kapea else 8,
                    color=TUMMA, rotation=90 if kapea else 0)
            bitit = (f"[{k.msb}]" if k.leveys == 1
                     else f"[{k.msb}:{k.lsb}]")
            selitteet.append(f"{k.nimi} {bitit}: {k.paasy}, "
                             f"nollaus {k.nollaus}")
        for bitti in range(bitteja):
            ax.text(bitteja - 1 - bitti + 0.5, 1.1, str(bitti),
                    ha="center", va="bottom", fontsize=6.5, color=HARMAA)
        ax.text(-0.3, 0.5, f"{r.nimi}\n0x{r.osoite:02X}", ha="right",
                va="center", fontsize=8, color=TUMMA)
        ax.text(0, -0.2, "     ".join(selitteet), ha="left", va="top",
                fontsize=7, color=HARMAA)
        ax.set(xlim=(-2.4, bitteja + 0.1), ylim=(-0.6, 1.45))
        ax.axis("off")
    tallenna(fig, polku)


KUVAT = {"historia": historia, "bittikentat": bittikentat}


def main() -> None:
    kohde = Path(sys.argv[1])
    kohde.mkdir(exist_ok=True)
    for nimi, piirra in KUVAT.items():
        piirra(kohde / f"{nimi}.png")
        print(f"kuvat/{nimi}.png")


if __name__ == "__main__":
    main()
