"""Pelkkä salaus ei suojaa eheyttä: CTR-tilan viestiä voi muokata."""

import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def salaa(avain: bytes, nonce: bytes, data: bytes) -> bytes:
    salain = Cipher(algorithms.AES(avain), modes.CTR(nonce)).encryptor()
    return salain.update(data) + salain.finalize()


def main() -> None:
    avain, nonce = os.urandom(32), os.urandom(16)
    viesti = b"maksa 0100 EUR tilille FI21123456"
    salattu = salaa(avain, nonce, viesti)

    # @alku hyokkays
    # Hyökkääjä ei tunne avainta, mutta tietää viestin muodon:
    # summa on tavuissa 6..9. CTR-tilassa salattu = selvä XOR avainvirta,
    # joten selvätekstin tavua voi muuttaa XORaamalla salattua.
    muokattu = bytearray(salattu)
    for i, (vanha, uusi) in enumerate(zip(b"0100", b"9100", strict=True)):
        muokattu[6 + i] ^= vanha ^ uusi
    # @loppu hyokkays

    # CTR-purku on sama operaatio kuin salaus.
    purettu = salaa(avain, nonce, bytes(muokattu))
    print("vastaanottaja purkaa:", purettu.decode())


if __name__ == "__main__":
    main()
