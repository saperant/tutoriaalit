"""Opetusesimerkki: täyteoraakkelihyökkäys CBC-tilaa vastaan.

Palvelin kertoo vain, oliko purettu täyte kelvollinen. Se riittää koko
viestin purkamiseen ilman avainta.
"""

import os

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

AVAIN = os.urandom(16)


def salaa(data: bytes) -> bytes:
    iv = os.urandom(16)
    taytin = padding.PKCS7(128).padder()
    taytetty = taytin.update(data) + taytin.finalize()
    salain = Cipher(algorithms.AES(AVAIN), modes.CBC(iv)).encryptor()
    return iv + salain.update(taytetty) + salain.finalize()


# @alku oraakkeli
def palvelin_hyvaksyy(salattu: bytes) -> bool:
    """Virheviesti, joka erottaa täytevirheen muista virheistä."""
    purkaja = Cipher(algorithms.AES(AVAIN),
                     modes.CBC(salattu[:16])).decryptor()
    selva = purkaja.update(salattu[16:]) + purkaja.finalize()
    poistaja = padding.PKCS7(128).unpadder()
    try:
        poistaja.update(selva) + poistaja.finalize()
    except ValueError:
        return False          # "virheellinen täyte"
    return True               # "virheellinen istunto" tms.
# @loppu oraakkeli


# @alku hyokkays
def pura_lohko(edellinen: bytes, lohko: bytes) -> bytes:
    """Purkaa yhden lohkon kyselemällä oraakkelia (enintään 16·256 kertaa)."""
    valitila = bytearray(16)   # AES-purun tulos ennen XORia
    for kohta in range(15, -1, -1):
        tayte = 16 - kohta
        for arvaus in range(256):
            vaarennos = bytearray(16)
            vaarennos[kohta] = arvaus
            for j in range(kohta + 1, 16):
                vaarennos[j] = valitila[j] ^ tayte
            if not palvelin_hyvaksyy(bytes(vaarennos) + lohko):
                continue
            if kohta == 15:   # varmistetaan, ettei täyte ollut 02 02
                vaarennos[14] ^= 1
                if not palvelin_hyvaksyy(bytes(vaarennos) + lohko):
                    continue
            valitila[kohta] = arvaus ^ tayte
            break
    return bytes(v ^ e for v, e in zip(valitila, edellinen, strict=True))
# @loppu hyokkays


def main() -> None:
    salattu = salaa(b"istunto=7f3a9c; rooli=yllapitaja")
    lohkot = [salattu[i:i + 16] for i in range(0, len(salattu), 16)]
    selva = b"".join(pura_lohko(lohkot[i - 1], lohkot[i])
                     for i in range(1, len(lohkot)))
    print("purettu ilman avainta:", selva[:-selva[-1]].decode())


if __name__ == "__main__":
    main()
