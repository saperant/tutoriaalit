"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Data lasketaan
esimerkin esimerkit/09-tehoanalyysi.py funktioilla samalla siemenellä
ja samassa järjestyksessä kuin esimerkin pääohjelmassa, ja tulos
tarkistetaan esimerkin testattua tulostetta vasten.
"""

import importlib.util
import random
import sys
from pathlib import Path
from statistics import correlation

from matplotlib import rcParams
from matplotlib.figure import Figure

JUURI = Path(__file__).resolve().parent.parent
KOROSTUS = "#A14B7C"
HARMAA = "#9AA5A8"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False


def lataa(nimi: str):
    polku = JUURI / "esimerkit" / nimi
    spec = importlib.util.spec_from_file_location("esimerkki", polku)
    assert spec and spec.loader
    moduuli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(moduuli)
    return moduuli


def tehoanalyysi(polku: Path) -> None:
    """Korrelaatio jokaiselle 256 avainarvaukselle, 2000 mittausta."""
    e = lataa("09-tehoanalyysi.py")
    avain = 0x2B
    satunnainen = random.Random(7)       # kuten esimerkin main()
    korrelaatiot = {}
    for maskattu in (False, True):
        for n in (20, 100, 2000):
            syotteet = [satunnainen.getrandbits(8) for _ in range(n)]
            mitat = e.mittaa(avain, syotteet, maskattu, satunnainen)
        korrelaatiot[maskattu] = [
            abs(correlation([float(e.paino(e.SBOX[p ^ arvaus]))
                             for p in syotteet], mitat))
            for arvaus in range(256)]

    # Sama tulos kuin tulosteessa: maskaamaton oikein, maskattu väärin.
    tuloste = (JUURI / "esimerkit/09-tehoanalyysi.odotettu").read_text(
        "utf-8").splitlines()
    paras = {m: max(range(256), key=k.__getitem__)
             for m, k in korrelaatiot.items()}
    for maskattu, rivi in zip((False, True), tuloste):
        assert (paras[maskattu] == avain) == rivi.endswith(
            "2000 mittausta: oikein")

    fig = Figure(figsize=(6.2, 2.5), dpi=200, layout="constrained")
    akselit = fig.subplots(1, 2, sharey=True)
    for ax, maskattu in zip(akselit, (False, True)):
        k = korrelaatiot[maskattu]
        varit = [KOROSTUS if a == avain else HARMAA for a in range(256)]
        ax.bar(range(256), k, width=1.0, color=varit)
        ax.bar([avain], [k[avain]], width=3.0, color=KOROSTUS)
        ax.set_title("maskattu toteutus" if maskattu
                     else "maskaamaton toteutus", fontsize=9)
        ax.set_xlabel("avaintavun arvaus")
        ax.set_xlim(0, 255)
        ax.set_xticks([0, 0x2B, 128, 255], ["0", "0x2B", "128", "255"])
        ax.annotate("oikea avain", (avain, k[avain]),
                    xytext=(avain + 30, max(k[avain], 0.12)),
                    fontsize=8, color=KOROSTUS,
                    arrowprops={"arrowstyle": "-", "color": KOROSTUS,
                                "linewidth": 0.6})
    akselit[0].set_ylabel("|korrelaatio|")
    fig.savefig(polku / "tehoanalyysi.png")


def main() -> None:
    kohde = Path(sys.argv[1])
    kohde.mkdir(exist_ok=True)
    tehoanalyysi(kohde)


if __name__ == "__main__":
    main()
