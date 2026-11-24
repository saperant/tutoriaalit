"""Pikaoppaan reseptit: oikeat oletusvalinnat yhdessä tiedostossa."""

import hashlib
import hmac
import os
import secrets

from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def main() -> None:
    # @alku satunnaisuus
    tunniste = secrets.token_urlsafe(32)
    avain = AESGCM.generate_key(bit_length=256)
    # @loppu satunnaisuus

    # @alku aead
    nonce = os.urandom(12)
    salattu = AESGCM(avain).encrypt(nonce, b"data", b"konteksti")
    data = AESGCM(avain).decrypt(nonce, salattu, b"konteksti")
    # @loppu aead

    # @alku mac
    tag = hmac.new(avain, b"viesti", hashlib.sha256).digest()
    ok = hmac.compare_digest(tag, hmac.new(avain, b"viesti",
                                           hashlib.sha256).digest())
    # @loppu mac

    # @alku salasana
    phc = Argon2id(salt=os.urandom(16), length=32, iterations=2, lanes=1,
                   memory_cost=19 * 1024).derive_phc_encoded(b"salasana")
    try:
        Argon2id.verify_phc_encoded(b"salasana", phc)
    except InvalidKey:
        ok = False
    # @loppu salasana

    # @alku allekirjoitus
    sk = Ed25519PrivateKey.generate()
    sig = sk.sign(b"julkaisu")
    sk.public_key().verify(sig, b"julkaisu")   # InvalidSignature
    # @loppu allekirjoitus

    # @alku vaihto
    a, b = X25519PrivateKey.generate(), X25519PrivateKey.generate()
    jaettu = a.exchange(b.public_key())
    istunto = HKDF(hashes.SHA256(), 32, salt=None,
                   info=b"sovellus v1").derive(jaettu)
    # @loppu vaihto

    print(len(tunniste), data.decode(), ok, len(istunto))


if __name__ == "__main__":
    main()
