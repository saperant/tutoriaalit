"""Simulaatiolokin yhteenveto: montako viestiä kustakin tasosta ja
komponentista. Lukee lokin syötteestä ja kirjoittaa yhteenvedon.

Käyttö:  python3 01-yhteenveto.py < simulaatio.log
"""

import sys
from collections import Counter
from collections.abc import Iterable, Sequence

# @alku jasenna
TASOT = ("INFO", "WARNING", "ERROR", "FATAL")


def jasenna(rivi: str) -> tuple[str, str] | None:
    """Palauttaa (taso, komponentti) riviltä '@ 120 ns TASO komp: ...'.

    Muut rivit (tyhjät, simulaattorin omat ilmoitukset) ohitetaan.
    """
    osat = rivi.split(maxsplit=5)
    if len(osat) < 5 or osat[0] != "@" or osat[3] not in TASOT:
        return None
    return osat[3], osat[4].rstrip(":")
# @loppu jasenna


# @alku yhteenveto
def yhteenveto(rivit: Iterable[str]) -> tuple[Counter[str], Counter[str]]:
    tasot: Counter[str] = Counter()
    komponentit: Counter[str] = Counter()
    for rivi in rivit:
        tulos = jasenna(rivi)
        if tulos is None:
            continue
        taso, komponentti = tulos
        tasot[taso] += 1
        if taso != "INFO":
            komponentit[komponentti] += 1
    return tasot, komponentit


def main(argv: Sequence[str]) -> int:
    del argv  # ei argumentteja vielä (ks. luku 2)
    tasot, komponentit = yhteenveto(sys.stdin)
    for taso in TASOT:
        print(f"{taso:<8}{tasot[taso]:>5}")
    print("varoitukset ja virheet komponenteittain:")
    for nimi, maara in komponentit.most_common():
        print(f"  {nimi:<12}{maara:>3}")
    return 1 if tasot["ERROR"] or tasot["FATAL"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
# @loppu yhteenveto
