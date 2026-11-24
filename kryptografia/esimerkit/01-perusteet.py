"""Autentikoitu salaus kirjastolla: salaus, purku ja muutoksen tunnistus."""

import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def main() -> None:
    # @alku salaus
    avain = AESGCM.generate_key(bit_length=256)  # säilytetään salassa
    aead = AESGCM(avain)
    nonce = os.urandom(12)  # uusi jokaiselle viestille
    viesti = b"Tilinumero FI21 1234 5600 0007 85"
    salattu = aead.encrypt(nonce, viesti, None)
    # @loppu salaus
    print(f"selväteksti {len(viesti)} tavua, salattu {len(salattu)} "
          f"tavua (+16 tavun tunniste)")

    # @alku purku
    purettu = aead.decrypt(nonce, salattu, None)
    print("purettu:", purettu.decode())

    muutettu = bytearray(salattu)
    muutettu[3] ^= 0x01  # hyökkääjä kääntää yhden bitin
    try:
        aead.decrypt(nonce, bytes(muutettu), None)
    except InvalidTag:
        print("muutettu viesti hylättiin (InvalidTag)")
    # @loppu purku


if __name__ == "__main__":
    main()
