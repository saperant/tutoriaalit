"""Mittaa kutsun hinnan ja piirtää kuvaajan. Käyttö:

    make -C esimerkit 09-hinta     # kääntää laajennuksen hakemistoon build/
    python3 kuvat/piirra.py kuvat

Mittaus on sama kuin esimerkissä esimerkit/09-hinta/main.py (samat
funktiot, sama data), mutta tässä tulostetaan ajat alkiota kohden
tiedostoon esimerkit/tulokset/09-hinta.txt ja piirretään niistä kuva.
Ajat riippuvat koneesta, joten skripti ajetaan käsin koneella, jossa ei
ole muuta kuormaa. Kuva ja tulostiedosto ovat versionhallinnassa.
"""

import sys
import time
from collections.abc import Callable
from pathlib import Path

import numpy as np
from matplotlib import rcParams
from matplotlib.figure import Figure

JUURI = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(JUURI / "esimerkit/build"))
import hinta  # noqa: E402  (käännetty laajennus, ks. yllä)

KOROSTUS = "#5B7A14"
HARMAA = "#5B6B70"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
N = 200_000


def nopein(f: Callable[[], object], kerrat: int = 15) -> float:
    paras = float("inf")
    for _ in range(kerrat):
        alku = time.perf_counter()
        f()
        paras = min(paras, time.perf_counter() - alku)
    return paras


def mittaa() -> list[tuple[str, float]]:
    """Palauttaa (nimi, nanosekuntia alkiota kohden) neljälle tavalle."""
    taulukko = np.random.default_rng(5).random(N)
    lista: list[float] = taulukko.tolist()
    tavat: list[tuple[str, Callable[[], object]]] = [
        ("Python: [x * x for x in lista]", lambda: [x * x for x in lista]),
        ("C++ alkio kerrallaan: nelio(x)",
         lambda: [hinta.nelio(x) for x in lista]),
        ("C++ lista kerralla: neliot_lista",
         lambda: hinta.neliot_lista(lista)),
        ("C++ taulukko kerralla: neliot_taulukko",
         lambda: hinta.neliot_taulukko(taulukko)),
    ]
    return [(nimi, nopein(f) / N * 1e9) for nimi, f in tavat]


def kirjoita(tulokset: list[tuple[str, float]]) -> None:
    rivit = [f"kutsun hinta, {N} alkiota, ns/alkio (paras 15 ajosta)"]
    taulukko = tulokset[-1][1]
    for nimi, ns in tulokset:
        rivit.append(f"  {nimi:<40}{ns:>7.2f}{ns / taulukko:>8.0f} x")
    polku = JUURI / "esimerkit/tulokset/09-hinta.txt"
    polku.parent.mkdir(exist_ok=True)
    polku.write_text("\n".join(rivit) + "\n", encoding="utf-8")


def piirra(tulokset: list[tuple[str, float]], kohde: Path) -> None:
    fig = Figure(figsize=(5.6, 2.2), dpi=200, layout="constrained")
    ax = fig.subplots()
    nimet = [nimi.replace(": ", "\n") for nimi, _ in tulokset]
    arvot = [ns for _, ns in tulokset]
    paikat = list(range(len(arvot)))[::-1]
    ax.barh(paikat, arvot, height=0.6,
            color=[HARMAA, KOROSTUS, KOROSTUS, KOROSTUS])
    ax.set_xscale("log")
    ax.set_xlim(0.3, max(arvot) * 4)
    ax.set_yticks(paikat, nimet, fontsize=8)
    ax.set_xlabel("nanosekuntia alkiota kohden (logaritminen)")
    for paikka, ns in zip(paikat, arvot, strict=True):
        teksti = f"{ns:.1f}".replace(".", ",")
        ax.annotate(teksti, (ns, paikka), xytext=(4, 0),
                    textcoords="offset points", va="center", fontsize=8)
    fig.savefig(kohde / "hinta.png", metadata={"Software": None})


def main() -> None:
    kohde = Path(sys.argv[1])
    tulokset = mittaa()
    kirjoita(tulokset)
    piirra(tulokset, kohde)


if __name__ == "__main__":
    main()
