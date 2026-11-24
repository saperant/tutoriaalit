"""Kertakäyttökoodit (TOTP, RFC 6238) ja niiden tarkistus."""

import hashlib
import hmac
import struct


# @alku totp
def hotp(avain: bytes, laskuri: int, numeroita: int = 6) -> str:
    """RFC 4226: HMAC laskurista, dynaaminen katkaisu, desimaaleiksi."""
    mac = hmac.new(avain, struct.pack(">Q", laskuri), hashlib.sha1).digest()
    alku = mac[-1] & 0x0F
    luku = struct.unpack(">I", mac[alku:alku + 4])[0] & 0x7FFFFFFF
    return str(luku % 10**numeroita).zfill(numeroita)


def totp(avain: bytes, aika: int, numeroita: int = 6) -> str:
    return hotp(avain, aika // 30, numeroita)   # 30 sekunnin jaksot
# @loppu totp


# @alku tarkistus
class Tarkistin:
    """Hyväksyy edellisen, nykyisen ja seuraavan jakson koodin (kellon
    heitto), mutta kunkin jakson vain kerran (uudelleenkäytön esto)."""

    def __init__(self, avain: bytes) -> None:
        self.avain = avain
        self.viimeisin = -1

    def tarkista(self, koodi: str, aika: int) -> bool:
        nyt = aika // 30
        for jakso in (nyt - 1, nyt, nyt + 1):
            if jakso <= self.viimeisin:
                continue
            if hmac.compare_digest(hotp(self.avain, jakso), koodi):
                self.viimeisin = jakso
                return True
        return False
# @loppu tarkistus


# RFC 6238:n liitteen B testivektorit (SHA-1, 8 numeroa).
AVAIN = b"12345678901234567890"
for aika, odotettu in [(59, "94287082"), (1111111109, "07081804"),
                       (1234567890, "89005924"), (2000000000, "69279037")]:
    print(aika, totp(AVAIN, aika, 8), totp(AVAIN, aika, 8) == odotettu)

t = Tarkistin(AVAIN)
koodi = totp(AVAIN, 1_700_000_000)
print("oikea koodi:", t.tarkista(koodi, 1_700_000_010))
print("sama koodi uudelleen:", t.tarkista(koodi, 1_700_000_015))
print("väärä koodi:", t.tarkista("000000", 1_700_000_040))
