"""DHCP-viestit (RFC 2131) ja pieni DHCP-asiakas.

Ilman argumentteja rakentaa ja jäsentää esimerkkiviestit. Komento
`asiakas LIITÄNTÄ MAC` hakee osoitteen oikealta palvelimelta
(08-dnsmasq.sh ajaa sen verkkonimiavaruudessa).
"""

import ipaddress
import socket
import struct
import sys
from dataclasses import dataclass, field

TAIKALUKU = b"\x63\x82\x53\x63"
DISCOVER, OFFER, REQUEST, ACK = 1, 2, 3, 5
NIMET = {DISCOVER: "DISCOVER", OFFER: "OFFER", REQUEST: "REQUEST",
         ACK: "ACK"}


# @alku viesti
@dataclass
class Viesti:
    op: int                       # 1 = pyyntö, 2 = vastaus
    xid: int                      # tapahtumatunniste
    mac: str
    yiaddr: str = "0.0.0.0"       # "your address": tarjottu osoite
    optiot: dict[int, bytes] = field(default_factory=dict)

    def koodaa(self) -> bytes:
        # op, laitteistotyyppi 1 (Ethernet), osoitteen pituus 6, hops,
        # xid, secs, liput (0x8000 = vastaa yleislähetyksenä),
        # ciaddr, yiaddr, siaddr, giaddr, chaddr (16 tavua),
        # sname (64) ja file (128).
        otsake = struct.pack(
            "!BBBBIHH4s4s4s4s16s64s128s", self.op, 1, 6, 0, self.xid, 0,
            0x8000, bytes(4), ipaddress.IPv4Address(self.yiaddr).packed,
            bytes(4), bytes(4), bytes.fromhex(self.mac.replace(":", "")),
            b"", b"")
        optiot = b"".join(struct.pack("!BB", k, len(v)) + v
                          for k, v in self.optiot.items())
        return otsake + TAIKALUKU + optiot + b"\xff"

    @staticmethod
    def pura(data: bytes) -> "Viesti":
        op, _, _, _, xid = struct.unpack("!BBBBI", data[:8])
        yiaddr = str(ipaddress.IPv4Address(data[16:20]))
        mac = data[28:34].hex(":")
        if data[236:240] != TAIKALUKU:
            raise ValueError("ei DHCP-viesti")
        optiot: dict[int, bytes] = {}
        i = 240
        while i < len(data) and data[i] != 0xFF:
            if data[i] == 0:          # täyte
                i += 1
                continue
            koodi, pituus = data[i], data[i + 1]
            optiot[koodi] = data[i + 2:i + 2 + pituus]
            i += 2 + pituus
        return Viesti(op, xid, mac, yiaddr, optiot)

    @property
    def tyyppi(self) -> str:
        return NIMET.get(self.optiot[53][0], "?")
# @loppu viesti


# @alku tulkinta
def kuvaile(v: Viesti) -> str:
    rivit = [f"{v.tyyppi} xid={v.xid:#010x} mac={v.mac}"]
    if v.yiaddr != "0.0.0.0":
        rivit.append(f"  osoite {v.yiaddr}")
    for koodi, nimi in [(1, "aliverkon maski"), (3, "reititin"),
                        (6, "nimipalvelin"), (54, "palvelin")]:
        if koodi in v.optiot:
            osoite = ipaddress.IPv4Address(v.optiot[koodi][:4])
            rivit.append(f"  {nimi} {osoite}")
    if 51 in v.optiot:
        (sekunnit,) = struct.unpack("!I", v.optiot[51])
        rivit.append(f"  vuokra {sekunnit} s")
    return "\n".join(rivit)
# @loppu tulkinta


def tarjous(pyynto: Viesti) -> Viesti:
    """Palvelimen tarjous esittelyä varten."""
    ip = ipaddress.IPv4Address
    return Viesti(2, pyynto.xid, pyynto.mac, "192.0.2.100", {
        53: bytes([OFFER]), 54: ip("192.0.2.1").packed,
        51: struct.pack("!I", 3600), 1: ip("255.255.255.0").packed,
        3: ip("192.0.2.1").packed, 6: ip("192.0.2.53").packed})


def esittely() -> None:
    # @alku esittely
    discover = Viesti(1, 0x3903F326, "02:00:00:00:00:0b",
                      optiot={53: bytes([DISCOVER]),
                              55: bytes([1, 3, 6, 51])})
    data = discover.koodaa()
    print(f"DISCOVER: {len(data)} tavua UDP:n hyötykuormana")
    print(kuvaile(Viesti.pura(data)))
    print(kuvaile(Viesti.pura(tarjous(discover).koodaa())))
    # @loppu esittely


# @alku asiakas
def hae_osoite(liitanta: str, mac: str) -> Viesti:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE,
                 liitanta.encode())
    s.bind(("", 68))
    s.settimeout(3)
    xid = 0x3903F326

    def kysy(viesti: Viesti, odotettu: int) -> Viesti:
        s.sendto(viesti.koodaa(), ("255.255.255.255", 67))
        while True:
            vastaus = Viesti.pura(s.recv(1500))
            if vastaus.xid == xid and vastaus.optiot[53][0] == odotettu:
                print(kuvaile(vastaus))
                return vastaus

    with s:
        tarjous = kysy(Viesti(1, xid, mac, optiot={
            53: bytes([DISCOVER]), 55: bytes([1, 3, 6, 51])}), OFFER)
        # REQUEST nimeää valitun palvelimen ja pyydetyn osoitteen.
        return kysy(Viesti(1, xid, mac, optiot={
            53: bytes([REQUEST]),
            50: ipaddress.IPv4Address(tarjous.yiaddr).packed,
            54: tarjous.optiot[54], 55: bytes([1, 3, 6, 51])}), ACK)
# @loppu asiakas


def main(argumentit: list[str]) -> None:
    if not argumentit:
        esittely()
    elif argumentit[0] == "asiakas":
        kuittaus = hae_osoite(argumentit[1], argumentit[2])
        maski = ipaddress.IPv4Address(kuittaus.optiot[1])
        pituus = ipaddress.IPv4Network(f"0.0.0.0/{maski}").prefixlen
        # Komentotulkki käyttää viimeistä riviä: osoite/pituus reititin.
        reititin = ipaddress.IPv4Address(kuittaus.optiot[3][:4])
        print(f"{kuittaus.yiaddr}/{pituus} {reititin}")
    else:
        sys.exit(f"tuntematon komento: {argumentit[0]}")


if __name__ == "__main__":
    main(sys.argv[1:])
