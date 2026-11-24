"""DNS- ja mDNS-asiakas.

Ilman argumentteja koodaa kyselyn ja purkaa esimerkkivastauksen.
Komennot (09-nimipalvelu.sh ja 09-mdns.sh käyttävät niitä):
  kysy PALVELIN NIMI TYYPPI
  mdns-vastaa NIMI OSOITE
  mdns-kysy NIMI
"""

import ipaddress
import socket
import struct
import sys

from dnsviesti import TYYPIT, kysely, pura, pura_nimi, vastaus

MDNS_RYHMA = "224.0.0.251"
MDNS_PORTTI = 5353


def tulosta(data: bytes) -> None:
    v = pura(data)
    print(f"vastaus {v.koodi}, tietueita {len(v.vastaukset)}")
    for t in v.vastaukset:
        print(f"  {t.nimi:22} {t.ttl:5} {t.tyyppi:5} {t.arvo}")


def esittely() -> None:
    # @alku esittely
    k = kysely("www.koti.example", "A", tunniste=0x1234)
    print(f"kysely {len(k)} tavua:")
    for alku in range(0, len(k), 16):
        print(f"  {k[alku:alku + 16].hex(' ')}")
    v = vastaus(k, [("", TYYPIT["A"],
                     ipaddress.IPv4Address("192.0.2.80").packed),
                    ("", TYYPIT["A"],
                     ipaddress.IPv4Address("192.0.2.81").packed)], ttl=300)
    print(f"vastaus {len(v)} tavua, nimi pakattuna osoittimella c0 0c")
    tulosta(v)
    # @loppu esittely


# @alku kysy
def kysy(palvelin: str, nimi: str, tyyppi: str) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(2)
        tunniste = 0x4242
        s.sendto(kysely(nimi, tyyppi, tunniste), (palvelin, 53))
        data, _ = s.recvfrom(4096)
        # Vastaus hyväksytään vain, jos tunniste täsmää: muuten kuka
        # tahansa voisi syöttää väärennettyjä vastauksia.
        if pura(data).tunniste != tunniste:
            raise ValueError("tunniste ei täsmää")
        tulosta(data)
# @loppu kysy


# @alku mdns
def mdns_sokeetti() -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", MDNS_PORTTI))
    # Liitytään ryhmään: kytkin ja verkkokortti päästävät läpi vain
    # ryhmälähetykset, joita joku kuuntelee.
    jasenyys = struct.pack("4s4s", socket.inet_aton(MDNS_RYHMA),
                           socket.inet_aton("0.0.0.0"))
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, jasenyys)
    return s


def mdns_vastaa(nimi: str, osoite: str) -> None:
    """Vastaa yhteen kyselyyn omasta nimestä ja lopettaa."""
    with mdns_sokeetti() as s:
        while True:
            data, _ = s.recvfrom(4096)
            if pura_kysymys(data) == nimi:
                rdata = ipaddress.IPv4Address(osoite).packed
                # mDNS-vastaus lähetetään ryhmään, jotta kaikki koneet
                # voivat päivittää välimuistinsa.
                s.sendto(vastaus(data, [("", TYYPIT["A"], rdata)], 120),
                         (MDNS_RYHMA, MDNS_PORTTI))
                return


def mdns_kysy(nimi: str) -> None:
    with mdns_sokeetti() as s:
        s.settimeout(2)
        s.sendto(kysely(nimi, "A", tunniste=0, rekursio=False),
                 (MDNS_RYHMA, MDNS_PORTTI))
        while True:
            data, (lahettaja, _) = s.recvfrom(4096)
            if struct.unpack("!H", data[2:4])[0] & 0x8000:   # QR: vastaus
                print(f"vastaaja {lahettaja}")
                tulosta(data)
                return
# @loppu mdns


def pura_kysymys(data: bytes) -> str:
    return pura_nimi(data, 12)[0]


def main(argumentit: list[str]) -> None:
    if not argumentit:
        esittely()
    elif argumentit[0] == "kysy":
        kysy(*argumentit[1:4])
    elif argumentit[0] == "mdns-vastaa":
        mdns_vastaa(argumentit[1], argumentit[2])
    elif argumentit[0] == "mdns-kysy":
        mdns_kysy(argumentit[1])
    else:
        sys.exit(f"tuntematon komento: {argumentit[0]}")


if __name__ == "__main__":
    main(sys.argv[1:])
