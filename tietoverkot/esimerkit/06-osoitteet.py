"""IPv6-osoitteet: esitystavat, tyypit, SLAAC ja ryhmälähetysosoitteet."""

import ipaddress


# @alku eui64
def eui64_tunniste(mac: str) -> bytes:
    """Liitännän tunniste MAC-osoitteesta (modifioitu EUI-64):
    keskelle ff:fe ja U/L-bitti (0x02) käännetään."""
    tavut = bytearray.fromhex(mac.replace(":", ""))
    tavut[0] ^= 0x02
    return bytes(tavut[:3]) + b"\xff\xfe" + bytes(tavut[3:])


def slaac(etuliite: str, mac: str) -> ipaddress.IPv6Address:
    verkko = ipaddress.IPv6Network(etuliite)
    if verkko.prefixlen != 64:
        raise ValueError("SLAAC edellyttää /64-etuliitettä")
    return ipaddress.IPv6Address(
        verkko.network_address.packed[:8] + eui64_tunniste(mac))
# @loppu eui64


# @alku ryhma
def pyyntoryhma(osoite: ipaddress.IPv6Address) -> ipaddress.IPv6Address:
    """Solicited-node-ryhmä: ff02::1:ff ja osoitteen 24 viimeistä bittiä.
    NDP-kysely lähetetään tähän ryhmään, ei kaikille."""
    return ipaddress.IPv6Address(
        bytes.fromhex("ff02" + "00" * 9 + "01ff") + osoite.packed[13:])


def ryhma_mac(ryhma: ipaddress.IPv6Address) -> str:
    """IPv6-ryhmälähetyksen Ethernet-osoite: 33:33 + 32 viimeistä bittiä."""
    return (b"\x33\x33" + ryhma.packed[12:]).hex(":")
# @loppu ryhma


def main() -> None:
    # @alku esitys
    for teksti in ["2001:0db8:0000:0000:0000:ff00:0042:8329",
                   "2001:db8:0:0:1:0:0:1", "fe80::1", "fd12:3456:789a::1",
                   "ff02::1", "::1"]:
        a = ipaddress.IPv6Address(teksti)
        tyyppi = ("linkkipaikallinen" if a.is_link_local else
                  "ryhmälähetys" if a.is_multicast else
                  "silmukka" if a.is_loopback else
                  "yksityinen (ULA)" if a in ipaddress.IPv6Network(
                      "fc00::/7") else
                  "dokumentaatio" if a in ipaddress.IPv6Network(
                      "2001:db8::/32") else "muu")
        print(f"{str(a):24} {tyyppi}")
    print(ipaddress.IPv6Address("2001:db8::1").exploded)
    # @loppu esitys

    # @alku kaytto
    mac = "02:00:00:00:00:0a"
    paikallinen = slaac("fe80::/64", mac)
    globaali = slaac("2001:db8:10:20::/64", mac)
    print(f"MAC {mac}")
    print(f"linkkipaikallinen {paikallinen}")
    print(f"SLAAC-osoite      {globaali}")
    ryhma = pyyntoryhma(globaali)
    print(f"NDP-kyselyryhmä   {ryhma}  MAC {ryhma_mac(ryhma)}")
    print(f"käänteinen nimi   {globaali.reverse_pointer[:22]}…")
    # @loppu kaytto


if __name__ == "__main__":
    main()
