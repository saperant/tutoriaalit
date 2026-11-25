"""Karakterisointitestien syötteet: kaikkien vaihtoehtojen yhdistelmät."""

from collections.abc import Callable
from itertools import product
from pathlib import Path

Rivit = list[tuple[str, int, int]]
Laskufunktio = Callable[[str, int, Rivit, str], str]

KULTAINEN = Path(__file__).with_name("kultainen.txt")

# @alku syotteet
ASIAKASTYYPIT = [1, 2]                      # 2 = kanta-asiakas
KOODIT = ["", "KESA", "SYKSY"]
KORIT: dict[str, Rivit] = {
    "tyhja": [],
    "pieni": [("kahvi", 549, 2)],
    "keski": [("kahvi", 549, 5), ("tee", 189, 3)],
    "paljous": [("kahvi", 549, 10)],
    "iso": [("kahvi", 549, 12), ("tee", 189, 30)],
    "rajalla": [("lahjakortti", 10000, 1)],
}

TAPAUKSET = [
    (f"tyyppi{tyyppi}-{koodi or 'eikoodia'}-{kori}", tyyppi, koodi, kori)
    for tyyppi, koodi, kori in product(ASIAKASTYYPIT, KOODIT, KORIT)
]


def tulosta(lasku: Laskufunktio, tyyppi: int, koodi: str, kori: str) -> str:
    return lasku("Testi Asiakas", tyyppi, KORIT[kori], koodi)
# @loppu syotteet


def tallennetut() -> dict[str, str]:
    """Lukee vertailuaineiston: otsikkorivi "== nimi" ja sen tuloste."""
    tulos: dict[str, str] = {}
    nimi = ""
    for rivi in KULTAINEN.read_text("utf-8").splitlines(keepends=True):
        if rivi.startswith("== "):
            nimi = rivi[3:].strip()
            tulos[nimi] = ""
        else:
            tulos[nimi] += rivi
    return tulos
