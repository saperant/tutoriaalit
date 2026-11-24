"""Salaus ilman eheyttä: salakirjoitusta voi muokata tietämättä avainta.

Esimerkissä on havainnollistava jonosalain (avainvirta XOR viesti).
Oikeat jonosalaimet, kuten AES-CTR ja ChaCha20, käyttäytyvät samoin.
Siksi käytetään todennettua salausta (AEAD), ks. taito Kryptografia.
"""

import secrets


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b, strict=True))


# @alku hyokkays
selkoteksti = b"MAKSA 0100 EUR TILILLE FI12 3456"
avainvirta = secrets.token_bytes(len(selkoteksti))   # vain lähettäjällä
salattu = xor(selkoteksti, avainvirta)

# Hyökkääjä tietää viestin muodon muttei avainta. Hän muuttaa summan
# kohdan: (vanha XOR uusi) XOR salattu = salattu uudella summalla.
muutos = xor(b"0100", b"9900")
muokattu = salattu[:6] + xor(salattu[6:10], muutos) + salattu[10:]

print(xor(muokattu, avainvirta).decode())   # vastaanottaja purkaa
# @loppu hyokkays
