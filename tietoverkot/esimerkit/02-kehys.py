"""Kapselointi: UDP-datagrammi IPv4-paketissa Ethernet-kehyksessä.

Rakentaa kehyksen tavu tavulta struct-modulilla, laskee tarkistussummat
ja jäsentää kehyksen takaisin kentiksi.
"""

import ipaddress
import struct
from dataclasses import dataclass


# @alku summa
def tarkistussumma(data: bytes) -> int:
    """Internetin tarkistussumma (RFC 1071): 16-bittisten sanojen
    yhden komplementin summan komplementti."""
    if len(data) % 2:
        data += b"\x00"
    sanat: tuple[int, ...] = struct.unpack(f"!{len(data) // 2}H", data)
    summa = sum(sanat)
    while summa >> 16:
        summa = (summa & 0xFFFF) + (summa >> 16)
    return ~summa & 0xFFFF
# @loppu summa


def mac(teksti: str) -> bytes:
    return bytes.fromhex(teksti.replace(":", ""))


# @alku rakennus
def udp(lahde: str, kohde: str, lportti: int, kportti: int,
        data: bytes) -> bytes:
    pituus = 8 + len(data)
    # Tarkistussumma lasketaan näennäisotsakkeen (IP-osoitteet,
    # protokolla ja pituus) ja koko datagrammin yli.
    naennais = struct.pack(
        "!4s4sBBH", ipaddress.IPv4Address(lahde).packed,
        ipaddress.IPv4Address(kohde).packed, 0, 17, pituus)
    otsake = struct.pack("!HHHH", lportti, kportti, pituus, 0)
    summa = tarkistussumma(naennais + otsake + data)
    return struct.pack("!HHHH", lportti, kportti, pituus, summa) + data


def ipv4(lahde: str, kohde: str, protokolla: int, sisalto: bytes,
         ttl: int = 64, tunniste: int = 1) -> bytes:
    versio_ihl = (4 << 4) | 5          # versio 4, otsake 5 × 32 bittiä
    pituus = 20 + len(sisalto)
    lippu_df = 0x4000                   # "älä pilko" (DF)
    otsake = struct.pack(
        "!BBHHHBBH4s4s", versio_ihl, 0, pituus, tunniste, lippu_df, ttl,
        protokolla, 0, ipaddress.IPv4Address(lahde).packed,
        ipaddress.IPv4Address(kohde).packed)
    summa = tarkistussumma(otsake)
    return otsake[:10] + struct.pack("!H", summa) + otsake[12:] + sisalto


def ethernet(kohde: str, lahde: str, tyyppi: int, sisalto: bytes) -> bytes:
    return mac(kohde) + mac(lahde) + struct.pack("!H", tyyppi) + sisalto
# @loppu rakennus


# @alku jasennys
@dataclass(frozen=True)
class Kehys:
    kohde_mac: str
    lahde_mac: str
    lahde_ip: str
    kohde_ip: str
    ttl: int
    lahde_portti: int
    kohde_portti: int
    data: bytes


def jasenna(kehys: bytes) -> Kehys:
    kohde, lahde, tyyppi = struct.unpack("!6s6sH", kehys[:14])
    if tyyppi != 0x0800:
        raise ValueError(f"ei IPv4: tyyppi {tyyppi:#06x}")
    ip = kehys[14:]
    ihl = (ip[0] & 0x0F) * 4
    if tarkistussumma(ip[:ihl]) != 0:
        raise ValueError("IPv4-otsakkeen tarkistussumma ei täsmää")
    ttl, protokolla = ip[8], ip[9]
    if protokolla != 17:
        raise ValueError(f"ei UDP: protokolla {protokolla}")
    lportti, kportti, pituus, _ = struct.unpack("!HHHH", ip[ihl:ihl + 8])
    return Kehys(
        kohde.hex(":"), lahde.hex(":"),
        str(ipaddress.IPv4Address(ip[12:16])),
        str(ipaddress.IPv4Address(ip[16:20])), ttl, lportti, kportti,
        ip[ihl + 8:ihl + pituus])
# @loppu jasennys


def main() -> None:
    # @alku kaytto
    viesti = b"lampotila=21.5"
    datagrammi = udp("192.0.2.10", "192.0.2.20", 40000, 9000, viesti)
    paketti = ipv4("192.0.2.10", "192.0.2.20", 17, datagrammi)
    kehys = ethernet("02:00:00:00:00:20", "02:00:00:00:00:10", 0x0800,
                     paketti)
    print(f"kehys {len(kehys)} tavua: Ethernet 14 + IPv4 20 + UDP 8"
          f" + data {len(viesti)}")
    for alku in range(0, len(kehys), 16):
        rivi = kehys[alku:alku + 16]
        print(f"{alku:04x}  {rivi.hex(' ')}")
    k = jasenna(kehys)
    print(f"{k.lahde_mac} -> {k.kohde_mac}")
    print(f"{k.lahde_ip}:{k.lahde_portti} -> {k.kohde_ip}:{k.kohde_portti}"
          f" ttl={k.ttl}")
    print(k.data.decode())
    # Yksikin muuttunut bitti paljastuu tarkistussummasta.
    vioittunut = bytearray(kehys)
    vioittunut[22] ^= 0x01
    try:
        jasenna(bytes(vioittunut))
    except ValueError as virhe:
        print(f"hylätty: {virhe}")
    # @loppu kaytto


if __name__ == "__main__":
    main()
