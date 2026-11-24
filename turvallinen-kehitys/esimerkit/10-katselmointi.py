"""Koodinomistajat ja kahden henkilön sääntö pull requestille.

CODEOWNERS-tiedosto kertoo, kenen hyväksyntä tarvitaan mihinkin
polkuun. Viimeinen osuva rivi voittaa. Haarasuojaus vaatii lisäksi,
ettei tekijä hyväksy omaa muutostaan.
"""

from fnmatch import fnmatchcase
from pathlib import Path

RYHMAT = {
    "@yritys/kehittajat": {"aino", "eero", "liisa", "matti"},
    "@yritys/tietoturva": {"liisa"},
    "@yritys/maksut": {"matti"},
    "@yritys/alusta": {"eero"},
}


# @alku omistajat
def lue(teksti: str) -> list[tuple[str, list[str]]]:
    saannot = []
    for rivi in teksti.splitlines():
        if rivi.strip() and not rivi.startswith("#"):
            malli, *omistajat = rivi.split()
            saannot.append((malli, omistajat))
    return saannot


def osuu(malli: str, polku: str) -> bool:
    if malli.endswith("/"):                   # hakemisto ja sen sisältö
        return ("/" + polku).startswith(malli) if malli.startswith("/") \
            else f"/{malli}" in f"/{polku}"
    if malli.startswith("/"):
        return fnmatchcase(polku, malli[1:])
    return fnmatchcase(polku.rsplit("/", 1)[-1], malli) \
        or fnmatchcase(polku, malli)


def omistajat(saannot: list[tuple[str, list[str]]],
              polku: str) -> list[str]:
    tulos: list[str] = []
    for malli, ryhmat in saannot:     # viimeinen osuma voittaa
        if osuu(malli, polku):
            tulos = ryhmat
    return tulos
# @loppu omistajat


# @alku saanto
def arvioi(saannot: list[tuple[str, list[str]]], tekija: str,
           tiedostot: list[str], hyvaksyjat: set[str]) -> list[str]:
    puuttuu = []
    muut = hyvaksyjat - {tekija}              # oma hyväksyntä ei kelpaa
    if not muut:
        puuttuu.append("ei hyväksyntää tekijän lisäksi")
    for polku in tiedostot:
        ryhmat = omistajat(saannot, polku)
        # Kuten GitHubissa: yksi hyväksyntä joltakin rivin omistajalta.
        if ryhmat and not any(RYHMAT[r] & muut for r in ryhmat):
            puuttuu.append(f"{polku}: tarvitaan {' tai '.join(ryhmat)}")
    return sorted(set(puuttuu))
# @loppu saanto


def main() -> None:
    teksti = (Path(__file__).parent / "10-CODEOWNERS").read_text("utf-8")
    saannot = lue(teksti)
    tapaukset = [
        ("aino", ["src/raportit/vienti.py"], {"eero"}),
        ("aino", ["src/maksut/kortti.py"], {"matti"}),
        ("aino", ["src/todennus/salasana.py"], {"eero"}),
        ("liisa", ["src/todennus/istunto.py"], {"liisa"}),
        ("matti", [".github/workflows/ci.yml", "requirements.txt"],
         {"eero"}),
    ]
    for tekija, tiedostot, hyvaksyjat in tapaukset:
        puutteet = arvioi(saannot, tekija, tiedostot, hyvaksyjat)
        tila = "voidaan yhdistää" if not puutteet else "estetty"
        print(f"{tekija}: {', '.join(tiedostot)}: {tila}")
        for p in puutteet:
            print(f"  - {p}")


if __name__ == "__main__":
    main()
