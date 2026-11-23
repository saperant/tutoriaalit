"""Komentotulkin käskyjen jäsennys rakenteellisella hahmonsovituksella."""

import shlex
import sys


# @alku match
def suorita(rivi: str, varasto: dict[str, int]) -> str:
    match shlex.split(rivi):
        case []:
            return ""
        case ["lisää", nimi, maara] if maara.isdigit():
            varasto[nimi] = varasto.get(nimi, 0) + int(maara)
            return f"{nimi}: {varasto[nimi]}"
        case ["lisää", *_]:
            return "virhe: käyttö: lisää NIMI MÄÄRÄ"
        case ["poista", nimi] if nimi in varasto:
            del varasto[nimi]
            return f"{nimi} poistettu"
        case ["poista", nimi]:
            return f"virhe: {nimi} ei ole varastossa"
        case ["listaa"]:
            return ", ".join(f"{n}={m}" for n, m in sorted(varasto.items()))
        case [komento, *_]:
            return f"virhe: tuntematon komento {komento!r}"
    return ""


varasto: dict[str, int] = {}
for rivi in sys.stdin:
    if tulos := suorita(rivi, varasto):    # mursuoperaattori
        print(tulos)
# @loppu match
