"""Malliratkaisu 11-1: Sarjataulukko."""

import sys


def laske_pisteet(rivit: list[str]) -> dict[str, int]:
    """Summaa pisteet joukkueittain riveistä 'joukkue;pisteet'."""
    pisteet: dict[str, int] = {}
    for rivi in rivit:
        if not rivi.strip():
            continue
        joukkue, maara = rivi.split(";")
        joukkue = joukkue.strip()
        pisteet[joukkue] = pisteet.get(joukkue, 0) + int(maara)
    return pisteet


def sarjataulukko(pisteet: dict[str, int]) -> list[tuple[str, int]]:
    """Järjestää joukkueet: pisteet laskevasti, sitten nimi."""
    return sorted(pisteet.items(), key=lambda pari: (-pari[1], pari[0]))


def main() -> int:
    rivit = sys.stdin.read().splitlines()
    taulukko = sarjataulukko(laske_pisteet(rivit))
    for sija, (joukkue, maara) in enumerate(taulukko, start=1):
        print(f"{sija}. {joukkue} {maara}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
