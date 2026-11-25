"""Malliratkaisu 11-2: Tuntiraportti."""

import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Kirjaus:
    paiva: str
    tekija: str
    tunnit: float


def jasenna_kirjaus(rivi: str) -> Kirjaus:
    """Jäsentää rivin 'päivä;tekijä;tunnit' tai nostaa ValueErrorin."""
    kentat = [kentta.strip() for kentta in rivi.split(";")]
    if len(kentat) != 3:
        raise ValueError(f"odotettiin 3 kenttää, saatiin {len(kentat)}")
    paiva, tekija, teksti = kentat
    try:
        tunnit = float(teksti.replace(",", "."))
    except ValueError:
        raise ValueError(f"virheellinen tuntimäärä '{teksti}'") from None
    if tunnit <= 0:
        raise ValueError(f"virheellinen tuntimäärä '{teksti}'")
    return Kirjaus(paiva, tekija, tunnit)


def lue_kirjaukset(rivit: list[str]) -> tuple[list[Kirjaus], list[str]]:
    """Palauttaa kelvolliset kirjaukset ja virheilmoitukset."""
    kirjaukset = []
    virheet = []
    for nro, rivi in enumerate(rivit, start=1):
        if not rivi.strip() or rivi.startswith("#"):
            continue
        try:
            kirjaukset.append(jasenna_kirjaus(rivi))
        except ValueError as virhe:
            virheet.append(f"Rivi {nro}: {virhe}")
    return kirjaukset, virheet


def tunnit_tekijoittain(kirjaukset: list[Kirjaus]) -> dict[str, float]:
    """Summaa tunnit tekijän nimen mukaan."""
    summat: dict[str, float] = {}
    for kirjaus in kirjaukset:
        summat[kirjaus.tekija] = (summat.get(kirjaus.tekija, 0.0)
                                  + kirjaus.tunnit)
    return summat


def raporttirivi(nimi: str, tunnit: float) -> str:
    """Muotoilee rivin, esimerkiksi 'Aino        12,5 h'."""
    return f"{nimi:<10}{tunnit:>6.1f} h".replace(".", ",")


def main() -> int:
    kirjaukset, virheet = lue_kirjaukset(sys.stdin.read().splitlines())
    summat = tunnit_tekijoittain(kirjaukset)
    for nimi in sorted(summat):
        print(raporttirivi(nimi, summat[nimi]))
    print(raporttirivi("Yhteensä", sum(summat.values())))
    for virhe in virheet:
        print(virhe)
    return 0


if __name__ == "__main__":
    sys.exit(main())
