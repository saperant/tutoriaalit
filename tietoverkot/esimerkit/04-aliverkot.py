"""Aliverkkosuunnitelma: osastot omiin aliverkkoihinsa (VLSM)."""

import ipaddress


# @alku perusteet
def kuvaile(verkko: ipaddress.IPv4Network) -> None:
    kaytettavat = verkko.num_addresses - 2 if verkko.prefixlen < 31 else (
        verkko.num_addresses)
    print(f"{str(verkko):16} {str(verkko.netmask):16}"
          f"{str(verkko.broadcast_address):14} {kaytettavat:5}")
# @loppu perusteet


# @alku suunnitelma
def suunnittele(osoitealue: str,
                tarpeet: dict[str, int]) -> dict[str, ipaddress.IPv4Network]:
    """Jakaa osoitealueen aliverkkoihin suurimmasta tarpeesta alkaen.

    Tarve on koneiden määrä; aliverkkoon tarvitaan lisäksi verkko- ja
    lähetysosoite. Suurimmat ensin, jotta lohkot asettuvat rajoilleen
    eikä väliin jää hukkaa.
    """
    vapaat = [ipaddress.IPv4Network(osoitealue)]
    tulos: dict[str, ipaddress.IPv4Network] = {}
    for nimi, koneet in sorted(tarpeet.items(), key=lambda t: -t[1]):
        pituus = 32 - (koneet + 2 - 1).bit_length()
        # Pienin vapaa lohko, johon tarve mahtuu.
        sopivat = [v for v in vapaat if v.prefixlen <= pituus]
        if not sopivat:
            raise ValueError(f"{nimi}: {koneet} konetta ei mahdu")
        lohko = max(sopivat, key=lambda v: (v.prefixlen,
                                            -int(v.network_address)))
        vapaat.remove(lohko)
        aliverkot = list(lohko.subnets(new_prefix=pituus))
        tulos[nimi] = aliverkot[0]
        vapaat.extend(lohko.address_exclude(aliverkot[0]))
    return tulos
# @loppu suunnitelma


def main() -> None:
    # @alku kaytto
    print(f"{'':12}{'aliverkko':16} {'maski':16}{'lähetysosoite':14}"
          f" {'koneita':>5}")
    print(f"{'koko alue':12}", end="")
    kuvaile(ipaddress.IPv4Network("10.20.0.0/22"))
    suunnitelma = suunnittele("10.20.0.0/22", {
        "toimisto": 300, "tuotanto": 120, "vieraat": 50,
        "palvelimet": 20, "reitinvalit": 2})
    for nimi, verkko in suunnitelma.items():
        print(f"{nimi:12}", end="")
        kuvaile(verkko)

    osoite = ipaddress.IPv4Address("10.20.2.77")
    kuuluu = [n for n, v in suunnitelma.items() if osoite in v]
    print(f"{osoite} kuuluu aliverkkoon: {', '.join(kuuluu)}")
    for teksti in ["10.1.2.3", "172.16.5.4", "192.168.1.1",
                   "169.254.1.1", "8.8.8.8"]:
        a = ipaddress.IPv4Address(teksti)
        print(f"{teksti:12} yksityinen={a.is_private!s:5}"
              f" maailmanlaajuinen={a.is_global}")
    # @loppu kaytto


if __name__ == "__main__":
    main()
