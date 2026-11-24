"""Laiteohjelmistokuvan rakennus ja allekirjoitus (isäntäkoneen työkalu).

Kuva = 256 tavun otsake + sovellus. Otsakkeen 80 ensimmäistä tavua
(taikaluku, versio, koko, varattu ja sovelluksen SHA-512) allekirjoitetaan
Ed25519:llä, ja allekirjoitus tallennetaan otsakkeeseen (laite/lahde/
otsake.h). Ilman argumentteja ohjelma ajaa esittelyn.

Komennot (laitteen Makefile käyttää niitä):
  julkinen SIEMEN               C-otsake julkisesta avaimesta
  kuva SIEMEN VERSIO SISÄÄN ULOS  allekirjoitettu kuva
  peukaloi KUVA                 muuttaa yhden sovelluksen tavun
  otp ARVO ULOS                 OTP-laskurin sisältö
"""

import hashlib
import struct
import sys
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)

TAIKA = 0x4B555641
OTSAKE = 256
ALLEKIRJOITETTU = 80


# @alku kuva
def rakenna_kuva(avain: Ed25519PrivateKey, versio: int,
                 sovellus: bytes) -> bytes:
    """Otsake + sovellus; allekirjoitus kattaa otsakkeen alkuosan."""
    tiiviste = hashlib.sha512(sovellus).digest()
    alku = struct.pack("<4I", TAIKA, versio, len(sovellus), 0)
    allekirjoitettava = alku + tiiviste
    assert len(allekirjoitettava) == ALLEKIRJOITETTU
    allekirjoitus = avain.sign(allekirjoitettava)
    otsake = allekirjoitettava + allekirjoitus
    return otsake.ljust(OTSAKE, b"\0") + sovellus
# @loppu kuva


# @alku tarkista
def tarkista_kuva(julkinen: Ed25519PublicKey, kuva: bytes) -> str:
    """Sama tarkistus kuin käynnistimessä, isäntäkoneella."""
    taika, versio, koko, _ = struct.unpack_from("<4I", kuva)
    if taika != TAIKA:
        return "ei kuva"
    try:
        julkinen.verify(kuva[80:144], kuva[:ALLEKIRJOITETTU])
    except InvalidSignature:
        return "allekirjoitus ei kelpaa"
    sovellus = kuva[OTSAKE:OTSAKE + koko]
    if hashlib.sha512(sovellus).digest() != kuva[16:80]:
        return "tiiviste ei täsmää"
    return f"kelpaa (versio {versio}, {koko} tavua)"
# @loppu tarkista


def avain(siemen: str) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(siemen))


def julkinen_c(siemen: str) -> str:
    raaka = avain(siemen).public_key().public_bytes(
        Encoding.Raw, PublicFormat.Raw)
    tavut = ", ".join(f"0x{b:02x}" for b in raaka)
    rivit = [tavut[i:i + 72] for i in range(0, len(tavut), 72)]
    return ("/* Generoitu: valmistajan julkinen avain. */\n"
            "#include <stdint.h>\n"
            "static const uint8_t JULKINEN_AVAIN[32] = {\n    "
            + "\n    ".join(r.strip() for r in rivit) + "\n};\n")


# @alku otp
def otp(arvo: int) -> bytes:
    """Termometrikoodi: arvo N = N alinta bittiä poltettuna."""
    return struct.pack("<I", (1 << arvo) - 1)
# @loppu otp


def esittely() -> None:
    # RFC 8032:n testiavain 1: julkinen, joten vain kokeiluihin.
    valmistaja = avain("9d61b19deffd5a60ba844af492ec2cc4"
                       "4449c5697b326919703bac031cae7f60")
    hyokkaaja = Ed25519PrivateKey.from_private_bytes(bytes(32))
    sovellus = bytes(range(256)) * 4
    kuva = rakenna_kuva(valmistaja, 3, sovellus)
    julkinen = valmistaja.public_key()
    print("Kuvan koko:", len(kuva), "tavua")
    print("Aito:", tarkista_kuva(julkinen, kuva))
    muutettu = bytearray(kuva)
    muutettu[OTSAKE + 100] ^= 0x01
    print("Sovellusta muutettu:", tarkista_kuva(julkinen, bytes(muutettu)))
    versio = bytearray(kuva)
    struct.pack_into("<I", versio, 4, 9)
    print("Versiota muutettu:", tarkista_kuva(julkinen, bytes(versio)))
    vieras = rakenna_kuva(hyokkaaja, 3, sovellus)
    print("Väärä avain:", tarkista_kuva(julkinen, vieras))
    print("OTP-laskuri 3:", otp(3).hex())


def main(argv: list[str]) -> int:
    if not argv:
        esittely()
    elif argv[0] == "julkinen":
        print(julkinen_c(argv[1]), end="")
    elif argv[0] == "kuva":
        sovellus = Path(argv[3]).read_bytes()
        Path(argv[4]).write_bytes(
            rakenna_kuva(avain(argv[1]), int(argv[2]), sovellus))
    elif argv[0] == "peukaloi":
        kuva = bytearray(Path(argv[1]).read_bytes())
        kuva[OTSAKE + 64] ^= 0x01
        Path(argv[1]).write_bytes(bytes(kuva))
    elif argv[0] == "otp":
        Path(argv[2]).write_bytes(otp(int(argv[1])))
    else:
        print("tuntematon komento", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
