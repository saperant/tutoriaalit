"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Historiat luetaan
testatun esimerkin 06-tarkistin.cpp lähdekoodista ja tarkistimen
tulokset tiedostosta 06-tarkistin.odotettu, joten kuva näyttää samat
operaatiot ja saman järjestyksen kuin teksti.
"""

import re
import sys
from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
KOROSTUS = "#546676"
HARMAA = "#5B6B70"
VAALEA = "#D5DCE3"
VIRHE = "#B4532A"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
METATIEDOT = {"Software": None}

Operaatio = tuple[int, bool, int, int, int | None]


def historiat() -> dict[str, list[Operaatio]]:
    """Jäsentää kutsut tulosta("nimi", {{asiakas, kirjoitus, arvo, alku,
    loppu}, ...}) esimerkin lähdekoodista."""
    lahde = (ESIMERKIT / "06-tarkistin.cpp").read_text(encoding="utf-8")
    osa = lahde.split("// @alku historiat")[1].split("// @loppu")[0]
    tulos: dict[str, list[Operaatio]] = {}
    for nimi, runko in re.findall(r'tulosta\("([^"]+)",\s*\{(.*?)\}\);',
                                  osa, flags=re.S):
        operaatiot: list[Operaatio] = []
        for a, k, v, alku, loppu in re.findall(
                r"\{(\d+), (true|false), (\d+), (\d+), (\w+)\}", runko):
            operaatiot.append((int(a), k == "true", int(v), int(alku),
                               None if loppu == "KESKEN" else int(loppu)))
        tulos[nimi] = operaatiot
    return tulos


def jarjestykset() -> dict[str, list[str] | None]:
    """Tarkistimen tulos: linearisointijärjestys tai None."""
    tulos: dict[str, list[str] | None] = {}
    rivit = (ESIMERKIT / "06-tarkistin.odotettu").read_text(
        encoding="utf-8").splitlines()
    for rivi in rivit:
        nimi = rivi[:32].strip()
        loppu = rivi[32:].strip()
        tulos[nimi] = None if loppu == "EI" else loppu.split()[1:]
    return tulos


def linearisoituvuus(polku: Path) -> None:
    """Kolme historiaa aikajanalla: palkki on operaation kesto, numero
    sen paikka tarkistimen löytämässä järjestyksessä."""
    valitut = [("lukuja kirjoituksen aikana", "linearisoituva"),
               ("uusi ja sitten vanha", "ei linearisoituva"),
               ("kaksi kirjoittajaa", "linearisoituva")]
    kaikki, tulokset = historiat(), jarjestykset()
    fig = Figure(figsize=(6.0, 3.9), dpi=200, layout="constrained")
    akselit = fig.subplots(len(valitut), 1)
    for ax, (nimi, tulos) in zip(akselit, valitut, strict=True):
        operaatiot = kaikki[nimi]
        jarjestys = tulokset[nimi]
        assert (jarjestys is None) == tulos.startswith("ei"), nimi
        jaljella = list(jarjestys or [])
        paikat: dict[int, int] = {}
        for sija, merkki in enumerate(jaljella, start=1):
            for i, (_, kirj, arvo, _, _) in enumerate(operaatiot):
                if i not in paikat and merkki == f"{'w' if kirj else 'r'}{arvo}":
                    paikat[i] = sija
                    break
        asiakkaat = sorted({o[0] for o in operaatiot})
        for i, (asiakas, kirj, arvo, alku, loppu) in enumerate(operaatiot):
            y = len(asiakkaat) - 1 - asiakkaat.index(asiakas)
            assert loppu is not None
            vari = KOROSTUS if kirj else VAALEA
            ax.barh(y, loppu - alku, left=alku, height=0.55, color=vari,
                    edgecolor=HARMAA, linewidth=0.6)
            teksti = f"{'kirjoita' if kirj else 'lue'} {arvo}"
            if i in paikat:
                teksti = f"{paikat[i]}.  {teksti}"
            ax.text((alku + loppu) / 2, y, teksti, ha="center", va="center",
                    fontsize=7.5, color="white" if kirj else "#1F2A2E")
        ax.set_yticks(range(len(asiakkaat)),
                      [f"asiakas {a}" for a in reversed(asiakkaat)])
        ax.set_ylim(-0.6, len(asiakkaat) - 0.4)
        ax.set_xlim(-2, 62)
        ax.tick_params(length=0, labelsize=8)
        for reuna in ("top", "right", "left"):
            ax.spines[reuna].set_visible(False)
        ax.set_title(f"{nimi}: {tulos}", loc="left", fontsize=9,
                     color=VIRHE if jarjestys is None else "#1F2A2E")
    akselit[-1].set_xlabel("aika")
    fig.savefig(polku, metadata=METATIEDOT)


KUVAT = {"linearisoituvuus": linearisoituvuus}


def main() -> None:
    kohde = Path(sys.argv[1])
    kohde.mkdir(exist_ok=True)
    for nimi, piirra in KUVAT.items():
        piirra(kohde / f"{nimi}.png")
        print(f"kuvat/{nimi}.png")


if __name__ == "__main__":
    main()
