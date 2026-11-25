"""Hyökkäyspuu: halvin tapa saavuttaa hyökkääjän tavoite."""

from __future__ import annotations

import math
from dataclasses import dataclass, field


# @alku puu
@dataclass
class Solmu:
    nimi: str
    hinta: float = 0.0       # lehden kustannus hyökkääjälle (€)
    tyyppi: str = "lehti"    # lehti, TAI (yksi riittää) tai JA (kaikki)
    lapset: list[Solmu] = field(default_factory=list)


def halvin(s: Solmu) -> tuple[float, list[str]]:
    """Halvimman hyökkäyksen hinta ja siihen tarvittavat lehdet."""
    if s.tyyppi == "lehti":
        return s.hinta, [s.nimi]
    tulokset = [halvin(lapsi) for lapsi in s.lapset]
    if s.tyyppi == "TAI":
        return min(tulokset, key=lambda t: t[0])
    return (sum(h for h, _ in tulokset),
            [askel for _, polku in tulokset for askel in polku])
# @loppu puu


# @alku esimerkki
varmuuskopio = Solmu("julkinen varmuuskopio pilvisäilössä", 500)
puu = Solmu("lue asiakastietokanta", tyyppi="TAI", lapset=[
    Solmu("SQL-injektio rajapinnassa", 5000),
    Solmu("ylläpitäjän tunnukset", tyyppi="JA", lapset=[
        Solmu("tietojenkalastelu", 2000),
        Solmu("MFA-väsytys (push-pommitus)", 1500),
    ]),
    varmuuskopio,
])
# @loppu esimerkki


def tulosta() -> None:
    hinta, polku = halvin(puu)
    print(f"Halvin hyökkäys {hinta:.0f} €: {' + '.join(polku)}")

    # Korjataan halvin kohta ja katsotaan, mihin hyökkääjä siirtyy.
    varmuuskopio.hinta = math.inf
    hinta, polku = halvin(puu)
    print(f"Korjauksen jälkeen {hinta:.0f} €: {' + '.join(polku)}")


if __name__ == "__main__":
    tulosta()
