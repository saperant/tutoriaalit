"""NDP: IPv6:n naapurikysely (Neighbor Solicitation), joka korvaa ARP:n."""

import ipaddress
import struct

ICMPV6 = 58


def tarkistussumma(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    sanat: tuple[int, ...] = struct.unpack(f"!{len(data) // 2}H", data)
    summa = sum(sanat)
    while summa >> 16:
        summa = (summa & 0xFFFF) + (summa >> 16)
    return ~summa & 0xFFFF


def pyyntoryhma(kohde: ipaddress.IPv6Address) -> ipaddress.IPv6Address:
    return ipaddress.IPv6Address(
        bytes.fromhex("ff02" + "00" * 9 + "01ff") + kohde.packed[13:])


# @alku kysely
def naapurikysely(lahde: str, kohde: str, lahde_mac: str) -> bytes:
    """Rakentaa IPv6-paketin, jossa on ICMPv6-naapurikysely."""
    src = ipaddress.IPv6Address(lahde)
    tgt = ipaddress.IPv6Address(kohde)
    dst = pyyntoryhma(tgt)
    # Tyyppi 135, koodi 0, summa, varattu; kohdeosoite; optio 1 =
    # lähettäjän linkkikerroksen osoite (pituus 1 × 8 tavua).
    optio = struct.pack("!BB6s", 1, 1, bytes.fromhex(lahde_mac.replace(
        ":", "")))
    viesti = struct.pack("!BBHI16s", 135, 0, 0, 0, tgt.packed) + optio
    naennais = struct.pack("!16s16sI3xB", src.packed, dst.packed,
                           len(viesti), ICMPV6)
    summa = tarkistussumma(naennais + viesti)
    viesti = viesti[:2] + struct.pack("!H", summa) + viesti[4:]
    # IPv6-otsake: versio 6, liikenneluokka ja vuo 0, hyötykuorman
    # pituus, seuraava otsake ICMPv6, hyppyraja 255 (NDP vaatii).
    otsake = struct.pack("!IHBB16s16s", 6 << 28, len(viesti), ICMPV6, 255,
                         src.packed, dst.packed)
    return otsake + viesti
# @loppu kysely


# @alku jasennys
def jasenna(paketti: bytes) -> str:
    versio = paketti[0] >> 4
    pituus, seuraava, hyppyraja = struct.unpack("!HBB", paketti[4:8])
    src = ipaddress.IPv6Address(paketti[8:24])
    dst = ipaddress.IPv6Address(paketti[24:40])
    viesti = paketti[40:40 + pituus]
    naennais = struct.pack("!16s16sI3xB", src.packed, dst.packed,
                           len(viesti), seuraava)
    ok = tarkistussumma(naennais + viesti) == 0
    tyyppi = viesti[0]
    kohde = ipaddress.IPv6Address(viesti[8:24])
    mac = viesti[26:32].hex(":")
    return (f"IPv{versio} {src} > {dst} hyppyraja {hyppyraja}\n"
            f"ICMPv6 tyyppi {tyyppi}: kuka on {kohde}? kerro {mac}"
            f" (summa {'ok' if ok else 'VIRHE'})")
# @loppu jasennys


def main() -> None:
    paketti = naapurikysely("fe80::ff:fe00:a", "fe80::ff:fe00:b",
                            "02:00:00:00:00:0a")
    print(f"{len(paketti)} tavua: IPv6-otsake 40 + ICMPv6 32")
    print(jasenna(paketti))


if __name__ == "__main__":
    main()
