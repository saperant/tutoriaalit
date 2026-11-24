"""Laiteohjelmistokuvan käsittely: tiedosto muistina, jonka alku on
tietyssä osoitteessa."""
import struct
from dataclasses import dataclass


@dataclass(frozen=True)
class Kuva:
    """Raaka binääri, joka on ladattu osoitteeseen kanta."""

    data: bytes
    kanta: int = 0

    @classmethod
    def lue(cls, polku: str, kanta: int = 0) -> "Kuva":
        with open(polku, "rb") as f:
            return cls(f.read(), kanta)

    @property
    def loppu(self) -> int:
        return self.kanta + len(self.data)

    def sisaltaa(self, osoite: int, pituus: int = 1) -> bool:
        return self.kanta <= osoite and osoite + pituus <= self.loppu

    def tavut(self, osoite: int, pituus: int) -> bytes:
        if not self.sisaltaa(osoite, pituus):
            raise ValueError(f"osoite {osoite:#x} kuvan ulkopuolella")
        alku = osoite - self.kanta
        return self.data[alku:alku + pituus]

    def u32(self, osoite: int) -> int:
        arvo: int = struct.unpack("<I", self.tavut(osoite, 4))[0]
        return arvo

    def u16(self, osoite: int) -> int:
        arvo: int = struct.unpack("<H", self.tavut(osoite, 2))[0]
        return arvo

    def merkkijono(self, osoite: int, maks: int = 64) -> str | None:
        """ASCII-merkkijono, joka päättyy nollatavuun, tai None."""
        if not self.sisaltaa(osoite):
            return None
        alku = osoite - self.kanta
        loppu = self.data.find(b"\0", alku, alku + maks)
        if loppu <= alku:
            return None
        teksti = self.data[alku:loppu]
        if not all(0x20 <= t < 0x7F or t == 0x0A for t in teksti):
            return None
        return teksti.decode("ascii")

    def sanat(self, alku: int, loppu: int) -> list[tuple[int, int]]:
        """Kaikki 4:llä jaolliset sanat väliltä [alku, loppu)."""
        return [(o, self.u32(o)) for o in range(alku, loppu - 3, 4)]


def heksa(data: bytes, osoite: int = 0, rivit: int = 4) -> list[str]:
    """Heksavedos xxd:n tapaan."""
    tulos = []
    for i in range(0, min(len(data), 16 * rivit), 16):
        rivi = data[i:i + 16]
        heksat = " ".join(rivi[j:j + 2].hex() for j in range(0, 16, 2))
        ascii_ = "".join(chr(t) if 0x20 <= t < 0x7F else "." for t in rivi)
        tulos.append(f"{osoite + i:08x}: {heksat:<39}  {ascii_}")
    return tulos
