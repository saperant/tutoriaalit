"""Turvallinen kanava: AEAD ei yksin estä toistoa, järjestyksen
vaihtoa eikä viestin palauttamista lähettäjälle."""

import os
import struct

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


# @alku kanava
def suunnan_avain(salaisuus: bytes, suunta: bytes) -> bytes:
    """Kummallekin suunnalle oma avain yhteisestä salaisuudesta."""
    return HKDF(hashes.SHA256(), 32, salt=None,
                info=b"kanava v1 " + suunta).derive(salaisuus)


class Lahettaja:
    def __init__(self, avain: bytes) -> None:
        self._aead = ChaCha20Poly1305(avain)
        self._numero = 0

    def laheta(self, viesti: bytes) -> bytes:
        # Järjestysnumero on nonce: se ei toistu, eikä sitä tarvitse
        # lähettää, koska vastaanottaja laskee samaa numeroa.
        nonce = struct.pack(">4xQ", self._numero)
        self._numero += 1
        return self._aead.encrypt(nonce, viesti, None)


class Vastaanottaja:
    def __init__(self, avain: bytes) -> None:
        self._aead = ChaCha20Poly1305(avain)
        self._numero = 0

    def vastaanota(self, tietue: bytes) -> bytes:
        nonce = struct.pack(">4xQ", self._numero)
        viesti = self._aead.decrypt(nonce, tietue, None)   # tai InvalidTag
        self._numero += 1         # kasvaa vain hyväksytystä tietueesta
        return viesti
# @loppu kanava


def kokeile(vastaanottaja: Vastaanottaja, tietue: bytes) -> str:
    try:
        return vastaanottaja.vastaanota(tietue).decode()
    except InvalidTag:
        return "hylätty"


def main() -> None:
    salaisuus = os.urandom(32)           # avaintenvaihdon tulos (luku 8)
    asiakas = Lahettaja(suunnan_avain(salaisuus, b"asiakas->palvelin"))
    palvelin = Vastaanottaja(suunnan_avain(salaisuus, b"asiakas->palvelin"))
    asiakkaan_vastaanotto = Vastaanottaja(
        suunnan_avain(salaisuus, b"palvelin->asiakas"))

    # @alku kokeet
    t0 = asiakas.laheta(b"siirto 100 EUR")
    t1 = asiakas.laheta(b"kuittaus")
    t2 = asiakas.laheta(b"lopetus")

    print("tietue 0:", kokeile(palvelin, t0))
    print("toisto (tietue 0 uudelleen):", kokeile(palvelin, t0))
    print("väärä järjestys (tietue 2 ennen 1:tä):", kokeile(palvelin, t2))
    print("tietue 1:", kokeile(palvelin, t1))
    print("tietue 2:", kokeile(palvelin, t2))
    print("palautus lähettäjälle (tietue 0):",
          kokeile(asiakkaan_vastaanotto, t0))
    # @loppu kokeet


if __name__ == "__main__":
    main()
