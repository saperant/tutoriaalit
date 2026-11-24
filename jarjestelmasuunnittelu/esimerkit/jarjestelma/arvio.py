"""Selkäpuolen laskujen apuvälineet: yksiköt ja pyöristys.

Arvion tarkoitus on mittaluokka, ei tarkka luku. Siksi tulokset
pyöristetään kahteen merkitsevään numeroon ja yksiköt valitaan niin,
että luku on välillä 1-999.
"""

from __future__ import annotations

import math

SEKUNTIA_PAIVASSA = 86_400
SEKUNTIA_VUODESSA = 365 * SEKUNTIA_PAIVASSA


def pyorista(arvo: float, numeroita: int = 2) -> float:
    """Pyöristys merkitseviin numeroihin: 123456 -> 120000."""
    if arvo == 0:
        return 0.0
    eksponentti = math.floor(math.log10(abs(arvo)))
    return round(arvo, numeroita - 1 - eksponentti)


def _yksikko(arvo: float, kerroin: float, yksikot: list[str]) -> str:
    i = 0
    while abs(arvo) >= kerroin and i < len(yksikot) - 1:
        arvo /= kerroin
        i += 1
    return f"{pyorista(arvo):g} {yksikot[i]}"


def tavut(arvo: float) -> str:
    """Tavut SI-etuliittein (kt = 1000 t), kuten levyjen koot."""
    return _yksikko(arvo, 1000, ["t", "kt", "Mt", "Gt", "Tt", "Pt"])


def bitit_s(tavua_s: float) -> str:
    """Kaista bitteinä sekunnissa, kuten verkkoyhteydet."""
    return _yksikko(tavua_s * 8, 1000,
                    ["bit/s", "kbit/s", "Mbit/s", "Gbit/s", "Tbit/s"])


def maara(arvo: float) -> str:
    """Määrä tuhansin ja miljoonin: 1 200 000 -> 1.2 milj."""
    return _yksikko(arvo, 1000, ["", "t.", "milj.", "mrd."]).rstrip()
