"""Piirtää tutoriaalin mittauskuvaajat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä: ajat riippuvat
koneesta ja vaihtelevat ajosta toiseen. Mittaukset ovat samat kuin
esimerkeissä 13-hinnat.py (jäsenyystesti) ja 12-prosessit.py
(alkulukujen laskenta), mutta eri alkiomäärillä ja työntekijämäärillä.
Esimerkkien testit tarkistavat vain suuruusluokan.
"""

import importlib
import sys
import time
import timeit
from collections.abc import Callable
from concurrent.futures import Executor, ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"
KOROSTUS = "#2F5F9A"          # alueen Perusta väri
TOINEN = "#B07A2A"
HARMAA = "#5B6B70"
MUSTE = "#1F2A2E"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
rcParams["text.color"] = MUSTE
rcParams["axes.edgecolor"] = HARMAA
rcParams["axes.labelcolor"] = MUSTE
rcParams["xtick.color"] = HARMAA
rcParams["ytick.color"] = HARMAA
METATIEDOT = {"Software": None}
TOISTOT = 7                   # jokaisesta mittauksesta pienin aika


def uusi(leveys: float = 4.6, korkeus: float = 2.8) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


def haun_kesto_ns(kokoelma: list[int] | set[int], toistot: int) -> float:
    """Haun `-1 in kokoelma` kesto: pienin viidestä mittauksesta."""
    ajat = timeit.repeat("-1 in kokoelma", globals={"kokoelma": kokoelma},
                         number=toistot, repeat=5)
    return min(ajat) / toistot * 1e9


def jasenyys(polku: Path) -> None:
    """Haun `x in kokoelma` kesto listalle ja joukolle (pahin tapaus:
    alkiota ei ole), alkiomäärän funktiona."""
    koot = [10, 100, 1_000, 10_000, 100_000]
    lista_ns, joukko_ns = [], []
    for n in koot:
        lista = list(range(n))
        joukko = set(lista)
        toistot = max(20, 2_000_000 // n)
        lista_ns.append(haun_kesto_ns(lista, toistot))
        joukko_ns.append(haun_kesto_ns(joukko, 1_000_000))
    fig = uusi()
    ax = fig.subplots()
    ax.loglog(koot, lista_ns, "o-", color=TOINEN, label="list: O(n)")
    ax.loglog(koot, joukko_ns, "s-", color=KOROSTUS, label="set: O(1)")
    ax.set_xlabel("alkioita kokoelmassa")
    ax.set_ylabel("yhden haun kesto (ns)")
    ax.grid(True, which="major", color="#D9E0E3", linewidth=0.6)
    ax.legend(frameon=False)
    fig.savefig(polku, metadata=METATIEDOT)


def aja(pooli: Executor, palat: list[tuple[int, int]],
        funktio: Callable[[int, int], int]) -> float:
    alku = time.perf_counter()
    tulos = sum(pooli.map(funktio, *zip(*palat, strict=True)))
    assert tulos == 17_984                 # sama kuin esimerkin tuloste
    return time.perf_counter() - alku


def rinnakkaisuus(polku: Path) -> None:
    """Esimerkin 12-prosessit työ 1–4 säikeellä ja 1–4 prosessilla."""
    sys.path.insert(0, str(ESIMERKIT))
    alkulukuja = importlib.import_module("12-prosessit").alkulukuja
    raja = 200_000
    palat = [(a, min(a + 25_000, raja)) for a in range(0, raja, 25_000)]
    maarat = [1, 2, 3, 4]
    saikeet, prosessit = [], []
    for n in maarat:
        with ThreadPoolExecutor(max_workers=n) as pooli:
            saikeet.append(min(aja(pooli, palat, alkulukuja)
                               for _ in range(TOISTOT)))
        with ProcessPoolExecutor(max_workers=n) as pooli:
            aja(pooli, palat, alkulukuja)          # prosessien käynnistys
            prosessit.append(min(aja(pooli, palat, alkulukuja)
                                 for _ in range(TOISTOT)))
    fig = uusi()
    ax = fig.subplots()
    ax.plot(maarat, saikeet, "o-", color=TOINEN, label="säikeet (GIL)")
    ax.plot(maarat, prosessit, "s-", color=KOROSTUS, label="prosessit")
    ihanne = [prosessit[0] / n for n in maarat]
    ax.plot(maarat, ihanne, ":", color=HARMAA, label="ihanne: aika / n")
    ax.set_xticks(maarat)
    ax.set_xlabel("säikeitä tai prosesseja")
    ax.set_ylabel("kesto (s)")
    ax.set_ylim(bottom=0)
    ax.grid(True, axis="y", color="#D9E0E3", linewidth=0.6)
    ax.legend(frameon=False)
    fig.savefig(polku, metadata=METATIEDOT)


KUVAT = {"jasenyys": jasenyys, "rinnakkaisuus": rinnakkaisuus}

if __name__ == "__main__":
    kohde = Path(sys.argv[1])
    kohde.mkdir(parents=True, exist_ok=True)
    for kuva in sys.argv[2:] or list(KUVAT):
        KUVAT[kuva](kohde / f"{kuva}.png")
