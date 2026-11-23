"""Kotitalouden budjettiraportti tiliotteesta (vakiosyöte)."""

import sys

from raportti import euroina, kuukausittain, suurimmat_menot
from tapahtuma import Tapahtuma, jasenna_rivi


def lue_tapahtumat(rivit: list[str]) -> tuple[list[Tapahtuma], list[str]]:
    """Palauttaa jäsennetyt tapahtumat ja virheilmoitukset."""
    tapahtumat = []
    virheet = []
    for numero, rivi in enumerate(rivit, start=1):
        if not rivi.strip() or rivi.startswith("#"):
            continue
        try:
            tapahtumat.append(jasenna_rivi(rivi))
        except ValueError as virhe:
            virheet.append(f"rivi {numero}: {virhe}")
    return tapahtumat, virheet


def main() -> int:
    tapahtumat, virheet = lue_tapahtumat(sys.stdin.readlines())
    print(f"{'Kuukausi':<10}{'Tulot':>12}{'Menot':>12}{'Netto':>12}")
    kuukaudet = kuukausittain(tapahtumat)
    for kuukausi, (tulot, menot) in sorted(kuukaudet.items()):
        print(f"{kuukausi:<10}{euroina(tulot):>12}{euroina(menot):>12}"
              f"{euroina(tulot + menot):>12}")
    print("Suurimmat menot:")
    for luokka, summa in suurimmat_menot(tapahtumat, 3):
        print(f"  {luokka:<10}{euroina(summa):>12}")
    for virhe in virheet:
        print(f"Ohitettu {virhe}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
