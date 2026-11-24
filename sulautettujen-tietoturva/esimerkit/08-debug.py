"""Debug-portin lukitus ja todennettu debug.

Malli mukailee yleistä mikrokontrollerien lukitustasojen (RDP)
logiikkaa: taso 0 on avoin, tasolla 1 flashia ei voi lukea debuggerilla
ja tason laskeminen pyyhkii flashin, taso 2 on pysyvä. Todennettu
debug avaa portin vain valmistajan allekirjoittamalla, laite- ja
istuntokohtaisella luvalla, joten huoltoa ei tarvitse estää kokonaan.
"""

import os
import struct
from dataclasses import dataclass, field

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


@dataclass
class Laite:
    sarja: int
    valmistaja: Ed25519PublicKey
    taso: int = 0
    flash: bytes = b"salainen avain ja ohjelma"
    haaste: bytes | None = None
    auki: bool = False
    kaytetyt: set[bytes] = field(default_factory=set)

    # @alku rdp
    def lue_flash(self) -> str:
        if self.taso == 0 or self.auki:
            return self.flash.decode()
        return "estetty"

    def aseta_taso(self, uusi: int) -> str:
        if self.taso == 2:
            return "taso 2 on pysyvä"
        if uusi < self.taso:                 # 1 -> 0
            self.flash = bytes(len(self.flash))   # massapyyhintä
        self.taso = uusi
        return f"taso {uusi}"
    # @loppu rdp

    # @alku todennettu
    def anna_haaste(self) -> bytes:
        self.haaste = os.urandom(16)
        return struct.pack("<I", self.sarja) + self.haaste

    def avaa(self, lupa: bytes, allekirjoitus: bytes) -> str:
        if self.haaste is None or lupa in self.kaytetyt:
            return "hylätty: ei voimassa olevaa haastetta"
        try:
            self.valmistaja.verify(allekirjoitus, lupa)
        except InvalidSignature:
            return "hylätty: allekirjoitus"
        sarja, haaste = struct.unpack("<I16s", lupa[:20])
        if sarja != self.sarja or haaste != self.haaste:
            return "hylätty: lupa on toiselle laitteelle tai istunnolle"
        self.kaytetyt.add(lupa)
        self.haaste = None                   # lupa käy kerran
        self.auki = True
        return "debug avattu: " + lupa[20:].decode()
    # @loppu todennettu


def main() -> None:
    valmistaja = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    laite = Laite(1001, valmistaja.public_key())
    print("Taso 0, flash:", laite.lue_flash())
    print("Asetus:", laite.aseta_taso(1), "– flash:", laite.lue_flash())
    print("Alennus:", laite.aseta_taso(0), "– flash pyyhitty:",
          laite.flash == bytes(len(laite.flash)))

    laite = Laite(1002, valmistaja.public_key())
    laite.aseta_taso(1)
    haaste = laite.anna_haaste()
    # Valmistajan palvelin tarkistaa huoltajan oikeudet ja allekirjoittaa.
    lupa = haaste + b"vain luku"
    allekirjoitus = valmistaja.sign(lupa)
    print("Oikea lupa:", laite.avaa(lupa, allekirjoitus))
    print("Sama lupa uudelleen:", laite.avaa(lupa, allekirjoitus))
    toinen = Laite(1003, valmistaja.public_key(), taso=1)
    toinen.anna_haaste()
    print("Lupa toiselle laitteelle:", toinen.avaa(lupa, allekirjoitus))
    vaarennetty = Ed25519PrivateKey.from_private_bytes(bytes(32))
    lupa2 = toinen.anna_haaste() + b"kaikki"
    print("Väärä allekirjoittaja:",
          toinen.avaa(lupa2, vaarennetty.sign(lupa2)))
    print("Taso 2:", toinen.aseta_taso(2), "– alennus:",
          toinen.aseta_taso(0))


if __name__ == "__main__":
    main()
