"""Webhook-viestin aitous: pelkkä tiiviste vai HMAC."""

import hashlib
import hmac
import secrets

AVAIN = secrets.token_bytes(32)   # jaettu maksupalvelun kanssa
viesti = b'{"tilaus": 1042, "tila": "maksettu", "summa": 4990}'


# @alku tarkistus
def allekirjoita(data: bytes) -> str:
    return hmac.new(AVAIN, data, hashlib.sha256).hexdigest()


def aito(data: bytes, tunniste: str) -> bool:
    # compare_digest vertaa vakioajassa: vertailun kesto ei paljasta,
    # monesko merkki meni väärin.
    return hmac.compare_digest(allekirjoita(data), tunniste)
# @loppu tarkistus


# @alku hyokkays
def aito_tiivisteella(data: bytes, tunniste: str) -> bool:
    """VIRHE: tiivisteen voi laskea kuka tahansa, avainta ei tarvita."""
    return hashlib.sha256(data).hexdigest() == tunniste


# Hyökkääjä muuttaa summaa ja laskee väärennökselle uuden tiivisteen.
vaarennos = viesti.replace(b"4990", b"10")
print("pelkkä tiiviste, väärennös:",
      aito_tiivisteella(vaarennos, hashlib.sha256(vaarennos).hexdigest()))
# @loppu hyokkays

tunniste = allekirjoita(viesti)
print("HMAC, alkuperäinen:", aito(viesti, tunniste))
print("HMAC, väärennös:", aito(vaarennos, tunniste))
print("HMAC, väärennös arvatulla tunnisteella:",
      aito(vaarennos, hashlib.sha256(vaarennos).hexdigest()))
