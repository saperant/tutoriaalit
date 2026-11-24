"""TLS 1.3:n avainaikataulun alku (RFC 8446, luku 7.1).

Kaikki TLS 1.3:n avaimet johdetaan HKDF:llä. Tarkistusarvot ovat
RFC 8448:n esimerkkikättelystä.
"""

import hashlib
import hmac
import struct

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand


# @alku label
def hkdf_extract(suola: bytes, ikm: bytes) -> bytes:
    return hmac.new(suola, ikm, hashlib.sha256).digest()


def expand_label(salaisuus: bytes, nimike: str, konteksti: bytes,
                 pituus: int) -> bytes:
    """HKDF-Expand-Label: nimike sidotaan johdettuun avaimeen."""
    taysi = b"tls13 " + nimike.encode()
    info = (struct.pack(">H", pituus) + bytes([len(taysi)]) + taysi
            + bytes([len(konteksti)]) + konteksti)
    return HKDFExpand(hashes.SHA256(), pituus, info).derive(salaisuus)


def derive_secret(salaisuus: bytes, nimike: str, viestit: bytes) -> bytes:
    """Sitoo avaimen kättelyn siihenastisiin viesteihin tiivisteellä."""
    return expand_label(salaisuus, nimike, hashlib.sha256(viestit).digest(),
                        32)
# @loppu label


def main() -> None:
    # @alku aikataulu
    nollat = bytes(32)
    early = hkdf_extract(nollat, nollat)          # ei esijaettua avainta
    derived = derive_secret(early, "derived", b"")
    # Seuraavaksi: handshake = hkdf_extract(derived, (EC)DHE-salaisuus),
    # josta johdetaan kättelyn liikenneavaimet, ja niistä edelleen
    # sovellusdatan avaimet.
    # @loppu aikataulu
    print("early secret täsmää:", early.hex().startswith("33ad0a1c607ec03b"))
    print("derived täsmää:", derived.hex().startswith("6f2615a108c702c5"))


if __name__ == "__main__":
    main()
