"""Saman avaimen ja noncen uudelleenkäyttö virtasalauksessa."""

import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def salaa(avain: bytes, nonce: bytes, data: bytes) -> bytes:
    salain = Cipher(algorithms.AES(avain), modes.CTR(nonce)).encryptor()
    return salain.update(data) + salain.finalize()


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b, strict=False))


def main() -> None:
    avain, nonce = os.urandom(32), os.urandom(16)
    # @alku virhe
    s1 = salaa(avain, nonce, b"Tapaaminen siirtyy torstaille.")
    s2 = salaa(avain, nonce, b"Uusi salasana: Kesa-2026-paja!")  # sama
    # @loppu virhe

    # @alku hyokkays
    # Avainvirta kumoutuu: s1 XOR s2 = p1 XOR p2. Kun toinen viesti on
    # tiedossa tai arvattavissa, toinen paljastuu ilman avainta.
    arvattu = b"Tapaaminen siirtyy torstaille."
    paljastunut = xor(xor(s1, s2), arvattu)
    print("toinen viesti:", paljastunut.decode())
    # @loppu hyokkays


if __name__ == "__main__":
    main()
