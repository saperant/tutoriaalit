"""Laitekohtaiset avaimet ja käyttötarkoitusten erottaminen.

Jokaisella laitteella on oma juuriavain (HUK, hardware unique key),
joka on poltettu OTP-muistiin tai johdettu PUF:sta. Siitä johdetaan
HKDF:llä eri avain jokaiseen käyttöön, joten yhden käytön vuoto ei
paljasta muita. Valmistaja voi johtaa saman laitekohtaisen avaimen
pääavaimesta ja sarjanumerosta (avaimen monipuolistus), joten
taustajärjestelmän ei tarvitse tallentaa jokaista avainta.
"""

import hashlib
import hmac

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


# @alku johda
def johda(juuri: bytes, kaytto: str, pituus: int = 32) -> bytes:
    """Käyttötarkoituskohtainen avain laitteen juuriavaimesta."""
    return HKDF(algorithm=hashes.SHA256(), length=pituus, salt=None,
                info=kaytto.encode()).derive(juuri)


def laiteavain(paaavain: bytes, sarjanumero: str) -> bytes:
    """Valmistajan pääavaimesta johdettu laitekohtainen avain."""
    return hmac.new(paaavain, sarjanumero.encode(),
                    hashlib.sha256).digest()
# @loppu johda


def sormenjalki(avain: bytes) -> str:
    return hashlib.sha256(avain).hexdigest()[:12]


def main() -> None:
    # Esimerkin pääavain on kiinteä; oikea on HSM:ssä tehtaalla.
    paaavain = bytes.fromhex("00112233445566778899aabbccddeeff" * 2)
    laitteet = ["SN-000117", "SN-000118"]
    for sarja in laitteet:
        huk = laiteavain(paaavain, sarja)
        print(f"{sarja}: HUK {sormenjalki(huk)}")
        for kaytto in ["tallennus/v1", "pilvi-tunnistus/v1",
                       "debug-avaus/v1"]:
            print(f"  {kaytto:20} {sormenjalki(johda(huk, kaytto))}")
    # Taustajärjestelmä johtaa saman avaimen ilman tallennusta.
    tausta = johda(laiteavain(paaavain, "SN-000117"), "pilvi-tunnistus/v1")
    laite = johda(laiteavain(paaavain, "SN-000117"), "pilvi-tunnistus/v1")
    print("Taustajärjestelmä ja laite samaa mieltä:",
          hmac.compare_digest(tausta, laite))


if __name__ == "__main__":
    main()
