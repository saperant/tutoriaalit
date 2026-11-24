"""Osoitesuunnitelman laskenta: segmentit saavat aliverkkonsa tarpeen
mukaan suurimmasta pienimpään, jotta lohkot asettuvat rajoilleen ilman
hukkaa. IPv6-etuliitteeseen upotetaan VLAN-numero, jolloin osoitteesta
näkee suoraan, mihin segmenttiin se kuuluu."""

import ipaddress
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Segmentti:
    nimi: str
    vlan: int
    laitteita: int          # arvio nyt
    kasvuvara: float = 2.0  # kerroin tulevalle kasvulle


def koko(s: Segmentti) -> int:
    """Pienin etuliitteen pituus, johon laitteet ja kasvuvara mahtuvat.
    Verkko- ja yleislähetysosoite sekä yhdyskäytävä vievät kolme."""
    tarve = math.ceil(s.laitteita * s.kasvuvara) + 3
    return 32 - math.ceil(math.log2(tarve))


def jaa(
    lohko: ipaddress.IPv4Network, segmentit: list[Segmentti]
) -> list[tuple[Segmentti, ipaddress.IPv4Network]]:
    vapaa = lohko.network_address
    tulos = []
    for s in sorted(segmentit, key=koko):     # suurin verkko ensin
        verkko = ipaddress.IPv4Network((vapaa, koko(s)))
        if not verkko.subnet_of(lohko):
            raise ValueError(f"{s.nimi}: lohko {lohko} ei riitä")
        tulos.append((s, verkko))
        vapaa = verkko.broadcast_address + 1
    return sorted(tulos, key=lambda p: p[0].vlan)


SEGMENTIT = [
    Segmentti("hallinta", 10, 20),
    Segmentti("toimisto", 20, 180),
    Segmentti("puhelimet", 30, 60),
    Segmentti("palvelimet", 40, 25, kasvuvara=3.0),
    Segmentti("vieraat", 90, 100, kasvuvara=1.5),
]


def main() -> None:
    v4 = ipaddress.IPv4Network("10.20.0.0/21")
    v6 = ipaddress.IPv6Network("2001:db8:20::/48")
    print(f"{'VLAN':>4}  {'segmentti':<11} {'IPv4':<16} {'yhdyskäytävä':<13}"
          " IPv6")
    for s, verkko in jaa(v4, SEGMENTIT):
        # /48:n neljäs 16-bittinen ryhmä on VLAN-numero heksana luettuna
        # desimaalina: VLAN 20 -> 2001:db8:20:20::/64.
        v6verkko = ipaddress.IPv6Network(
            (int(v6.network_address) + (int(str(s.vlan), 16) << 64), 64))
        yhdk = verkko.network_address + 1
        print(f"{s.vlan:>4}  {s.nimi:<11} {verkko!s:<16} {yhdk!s:<13}"
              f" {v6verkko}")
    kaytetty = sum(verkko.num_addresses for _, verkko in jaa(v4, SEGMENTIT))
    print(f"käytössä {kaytetty}/{v4.num_addresses} osoitetta")


if __name__ == "__main__":
    main()
