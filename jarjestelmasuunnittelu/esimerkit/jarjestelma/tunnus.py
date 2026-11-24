"""Lyhytosoitteen koodi: sekvenssin numero sekoitettuna ja base62:na.

Tietokannan sekvenssi antaa yksikäsitteisen numeron ilman
koordinointia sovelluspalvelinten välillä. Peräkkäiset numerot
paljastaisivat palvelun koon ja olisivat arvattavia, joten numero
sekoitetaan kääntyvällä kuvauksella: kertolasku parittomalla
vakiolla modulo 2^40 on bijektio. Sekoitus ei ole salausta; se vain
peittää järjestyksen.
"""

from __future__ import annotations

MERKIT = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
BITTEJA = 40                      # 2^40 = 1.1e12 linkkiä
MODULI: int = 2 ** BITTEJA
KERROIN = 0x9E3779B97F & (MODULI - 1) | 1   # pariton
KAANTEINEN: int = pow(KERROIN, -1, MODULI)
PITUUS = 7                        # 62^7 = 3.5e12 > 2^40


# @alku koodi
def koodi(numero: int) -> str:
    if not 0 < numero < MODULI:
        raise ValueError(f"numero ei mahdu {BITTEJA} bittiin: {numero}")
    x = numero * KERROIN % MODULI
    merkit = []
    for _ in range(PITUUS):
        x, jaannos = divmod(x, 62)
        merkit.append(MERKIT[jaannos])
    return "".join(reversed(merkit))


def numero(koodi: str) -> int:
    """Käänteinen: ValueError, jos koodi ei ole kelvollinen."""
    if len(koodi) != PITUUS or any(m not in MERKIT for m in koodi):
        raise ValueError(f"virheellinen koodi: {koodi!r}")
    x = 0
    for m in koodi:
        x = x * 62 + MERKIT.index(m)
    if x >= MODULI:
        raise ValueError(f"virheellinen koodi: {koodi!r}")
    return x * KAANTEINEN % MODULI
# @loppu koodi
