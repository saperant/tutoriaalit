"""AEAD: liitetty data sidotaan salattuun viestiin."""

import json
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import (
    AESGCM,
    ChaCha20Poly1305,
)


# @alku tietue
def salaa_tietue(aead: AESGCM, kayttaja: str, data: bytes) -> bytes:
    """Salaa tietueen ja sitoo sen käyttäjään liitettynä datana."""
    nonce = os.urandom(12)
    liite = json.dumps({"kayttaja": kayttaja, "v": 1}).encode()
    return nonce + aead.encrypt(nonce, data, liite)


def pura_tietue(aead: AESGCM, kayttaja: str, tietue: bytes) -> bytes:
    nonce, salattu = tietue[:12], tietue[12:]
    liite = json.dumps({"kayttaja": kayttaja, "v": 1}).encode()
    return aead.decrypt(nonce, salattu, liite)
# @loppu tietue


def main() -> None:
    aead = AESGCM(AESGCM.generate_key(bit_length=256))
    tietue = salaa_tietue(aead, "aino", b"henkilotunnus=010190-123A")
    print("aino purkaa:", pura_tietue(aead, "aino", tietue).decode())

    # @alku vaihto
    # Hyökkääjä kopioi Ainon salatun tietueen Bertan riviin.
    try:
        pura_tietue(aead, "bertta", tietue)
    except InvalidTag:
        print("bertta: tietue ei kuulu tälle käyttäjälle")
    # @loppu vaihto

    # @alku chacha
    chacha = ChaCha20Poly1305(ChaCha20Poly1305.generate_key())
    nonce = os.urandom(12)
    salattu = chacha.encrypt(nonce, b"sama rajapinta", b"otsake")
    print("ChaCha20-Poly1305:", chacha.decrypt(nonce, salattu, b"otsake"))
    # @loppu chacha


if __name__ == "__main__":
    main()
