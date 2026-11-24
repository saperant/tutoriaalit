"""Salasanojen tallennus: suola ja hidas avaimenjohtofunktio (scrypt)."""

import hashlib
import hmac
import secrets

# scryptin parametrit: n kasvattaa laskenta- ja muistityötä.
N, R, P = 2**14, 8, 1


# @alku tallennus
def tiivista(salasana: str) -> str:
    suola = secrets.token_bytes(16)
    avain = hashlib.scrypt(salasana.encode(), salt=suola,
                           n=N, r=R, p=P, dklen=32)
    return f"scrypt${N}${R}${P}${suola.hex()}${avain.hex()}"


def tarkista(salasana: str, tallennettu: str) -> bool:
    _, n, r, p, suola, avain = tallennettu.split("$")
    laskettu = hashlib.scrypt(salasana.encode(), salt=bytes.fromhex(suola),
                              n=int(n), r=int(r), p=int(p), dklen=32)
    return hmac.compare_digest(laskettu.hex(), avain)
# @loppu tallennus


aino = tiivista("kesä2026!")
pekka = tiivista("kesä2026!")    # sama salasana kuin Ainolla
print("oikea salasana:", tarkista("kesä2026!", aino))
print("väärä salasana:", tarkista("kesä2025!", aino))
print("samat tiivisteet samasta salasanasta:", aino == pekka)
print("parametrit tallessa:", aino.split("$")[:4])
