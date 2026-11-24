"""Mittauskäynnistys ja etätodennus.

Turvallinen käynnistys pysäyttää laitteen, jos kuva ei kelpaa.
Mittauskäynnistys ei pysäytä vaan kirjaa: jokainen vaihe mittaa
(tiivistää) seuraavan ennen sen ajamista ja laajentaa mittauksen
rekisteriin, jota ei voi asettaa vaan ainoastaan laajentaa
(PCR, platform configuration register). Etätodentaja pyytää laitteelta
allekirjoitetun lainauksen (quote) ja päättää itse, luottaako se.
"""

import hashlib
import os
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


# @alku pcr
class Pcr:
    """Rekisteri, jota voi vain laajentaa: uusi = H(vanha ‖ mittaus)."""

    def __init__(self) -> None:
        self.arvo = bytes(32)

    def laajenna(self, mittaus: bytes) -> None:
        self.arvo = sha256(self.arvo + mittaus)
# @loppu pcr


@dataclass
class Laite:
    avain: Ed25519PrivateKey     # todennusavain, ei poistu laitteesta
    pcr: Pcr
    loki: list[tuple[str, bytes]]

    # @alku kaynnistys
    def kaynnista(self, vaiheet: list[tuple[str, bytes]]) -> None:
        for nimi, koodi in vaiheet:
            mittaus = sha256(koodi)
            self.pcr.laajenna(mittaus)
            self.loki.append((nimi, mittaus))
    # @loppu kaynnistys

    def lainaus(self, nonce: bytes) -> tuple[bytes, bytes]:
        return self.pcr.arvo, self.avain.sign(nonce + self.pcr.arvo)


# @alku todentaja
def todenna(julkinen: Ed25519PublicKey, nonce: bytes,
            pcr: bytes, allekirjoitus: bytes,
            loki: list[tuple[str, bytes]],
            hyvaksytyt: set[bytes]) -> str:
    try:
        julkinen.verify(allekirjoitus, nonce + pcr)
    except InvalidSignature:
        return "lainauksen allekirjoitus tai nonce ei kelpaa"
    toisto = Pcr()
    for _, mittaus in loki:
        toisto.laajenna(mittaus)
    if toisto.arvo != pcr:
        return "loki ei vastaa PCR:ää (lokia on muokattu)"
    tuntemattomat = [n for n, m in loki if m not in hyvaksytyt]
    if tuntemattomat:
        return "tuntematon ohjelmisto: " + ", ".join(tuntemattomat)
    return "luotettu"
# @loppu todentaja


def main() -> None:
    aito = [("käynnistin", b"bootloader v5"), ("ydin", b"kernel 6.12"),
            ("sovellus", b"app 3.1")]
    hyvaksytyt = {sha256(k) for _, k in aito}

    def kokeile(nimi: str, vaiheet: list[tuple[str, bytes]],
                vaarenna_loki: bool = False, vanha: bool = False) -> None:
        laite = Laite(Ed25519PrivateKey.from_private_bytes(bytes(32)),
                      Pcr(), [])
        laite.kaynnista(vaiheet)
        nonce = os.urandom(16)
        pcr, allekirjoitus = laite.lainaus(b"vanha nonce" if vanha
                                           else nonce)
        loki = list(laite.loki)
        if vaarenna_loki:   # haittaohjelma kertoo ajaneensa aidot osat
            loki = [(n, sha256(k)) for n, k in aito]
        tulos = todenna(laite.avain.public_key(), nonce, pcr,
                        allekirjoitus, loki, hyvaksytyt)
        print(f"{nimi}: {tulos}")

    kokeile("Aito laite", aito)
    muutettu = aito[:2] + [("sovellus", b"app 3.1 + takaovi")]
    kokeile("Muutettu sovellus", muutettu)
    kokeile("Muutettu, väärennetty loki", muutettu, vaarenna_loki=True)
    kokeile("Toistettu vanha lainaus", aito, vanha=True)


if __name__ == "__main__":
    main()
