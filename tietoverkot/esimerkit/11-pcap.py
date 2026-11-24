"""pcap-kaappaustiedoston luku: tiedosto- ja pakettiotsakkeet.

Ilman argumentteja kirjoittaa pienen kaappauksen ja lukee sen. Argumenttina
annetun tiedoston (esim. tcpdump -w) se tiivistää pakettilistaksi.
"""

import ipaddress
import struct
import sys
import tempfile
from collections import Counter
from collections.abc import Iterator
from pathlib import Path

PROTOKOLLAT = {1: "ICMP", 6: "TCP", 17: "UDP"}


# @alku luku
def paketit(polku: Path) -> Iterator[bytes]:
    """Käy läpi pcap-tiedoston kehykset (Ethernet-linkkityyppi)."""
    with polku.open("rb") as f:
        otsake = f.read(24)
        taika = otsake[:4]
        # Taikaluku kertoo tavujärjestyksen.
        jarjestys = "<" if taika == b"\xd4\xc3\xb2\xa1" else ">"
        (linkkityyppi,) = struct.unpack(jarjestys + "I", otsake[20:24])
        if linkkityyppi != 1:
            raise ValueError(f"linkkityyppi {linkkityyppi} ei ole Ethernet")
        while tietue := f.read(16):
            _, _, tallennettu, _ = struct.unpack(jarjestys + "IIII",
                                                 tietue)
            yield f.read(tallennettu)
# @loppu luku


# @alku tiivistys
def tiivista(kehys: bytes) -> str:
    (tyyppi,) = struct.unpack("!H", kehys[12:14])
    if tyyppi == 0x0806:
        return "ARP"
    if tyyppi != 0x0800:
        return f"tyyppi {tyyppi:#06x}"
    ip = kehys[14:]
    ihl = (ip[0] & 0x0F) * 4
    lahde = ipaddress.IPv4Address(ip[12:16])
    kohde = ipaddress.IPv4Address(ip[16:20])
    protokolla = PROTOKOLLAT.get(ip[9], str(ip[9]))
    if protokolla in ("TCP", "UDP"):
        lp, kp = struct.unpack("!HH", ip[ihl:ihl + 4])
        return f"{protokolla} {lahde}:{lp} > {kohde}:{kp}"
    return f"{protokolla} {lahde} > {kohde}"
# @loppu tiivistys


def kirjoita_esimerkki(polku: Path) -> None:
    def kehys(protokolla: int, kohde: str, data: bytes) -> bytes:
        ip = struct.pack("!BBHHHBB2x4s4s", 0x45, 0, 20 + len(data), 0, 0,
                         64, protokolla,
                         ipaddress.IPv4Address("192.0.2.10").packed,
                         ipaddress.IPv4Address(kohde).packed)
        return bytes(6) + bytes(6) + b"\x08\x00" + ip + data
    kehykset = [kehys(17, "192.0.2.53", struct.pack("!HH4x", 40000, 53)),
                kehys(6, "192.0.2.80", struct.pack("!HH16x", 40001, 443)),
                kehys(1, "192.0.2.1", bytes(8))]
    with polku.open("wb") as f:
        # Tiedosto-otsake: taikaluku, versio 2.4, aikavyöhyke, tarkkuus,
        # kaappauspituus ja linkkityyppi 1 (Ethernet).
        f.write(struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
        for i, k in enumerate(kehykset):
            f.write(struct.pack("<IIII", 1_700_000_000 + i, 0, len(k),
                                len(k)))
            f.write(k)


def main(argumentit: list[str]) -> None:
    if argumentit:
        polku = Path(argumentit[0])
        laskuri = Counter(tiivista(k) for k in paketit(polku))
        for kuvaus, maara in sorted(laskuri.items()):
            print(f"{maara:3}  {kuvaus}")
        return
    with tempfile.TemporaryDirectory() as tmp:
        polku = Path(tmp) / "esimerkki.pcap"
        kirjoita_esimerkki(polku)
        print(f"{polku.stat().st_size} tavua")
        for k in paketit(polku):
            print(tiivista(k))


if __name__ == "__main__":
    main(sys.argv[1:])
