"""Konvoluutiokoodi (7, 5), muistipituus 2, ja Viterbi-dekooderi.

Kaikki funktiot käsittelevät kerralla monta lohkoa: taulukon rivi on
yksi lohko. Koodi päätetään kahdella nollabitillä, joten kooderi palaa
tilaan 0 ja dekooderi tietää, mihin tilaan polku päättyy.
"""

from typing import Any

import numpy as np
import numpy.typing as npt

Bitit = npt.NDArray[np.int64]
Reaali = npt.NDArray[np.floating[Any]]

# @alku trellis
# Tila on kaksi edellistä bittiä (u[n-1] << 1) | u[n-2].
TILOJA = 4
SEURAAVA = np.array([[(u << 1) | (s >> 1) for u in (0, 1)]
                     for s in range(TILOJA)])
ULOS = np.array([[(u ^ (s >> 1) ^ (s & 1), u ^ (s & 1)) for u in (0, 1)]
                 for s in range(TILOJA)])   # generaattorit 111 ja 101


def koodaa(u: Bitit) -> Bitit:
    """Lohkot (B, L) -> koodibitit (B, 2 (L + 2)); nopeus noin 1/2."""
    B, L = u.shape
    tila = np.zeros(B, dtype=np.int64)
    c = np.empty((B, 2 * (L + 2)), dtype=np.int64)
    u = np.hstack([u, np.zeros((B, 2), dtype=np.int64)])  # päätösbitit
    for n in range(L + 2):
        c[:, 2 * n: 2 * n + 2] = ULOS[tila, u[:, n]]
        tila = SEURAAVA[tila, u[:, n]]
    return c
# @loppu trellis


# @alku viterbi
def viterbi(y: Reaali, pehmea: bool) -> Bitit:
    """Suurimman uskottavuuden polku. y: BPSK-näytteet (+1 = bitti 0).

    Pehmeä päätös käyttää näytteiden arvoja (euklidinen metriikka), kova
    vain merkkejä (Hamming-etäisyys).
    """
    B, n = y.shape
    askelia = n // 2
    if not pehmea:
        y = np.where(y < 0, -1.0, 1.0)
    x = 1.0 - 2 * ULOS                        # (tila, u, 2): odotetut arvot
    metriikka = np.full((B, TILOJA), np.inf)
    metriikka[:, 0] = 0.0
    edeltaja = np.empty((askelia, B, TILOJA), dtype=np.int64)
    for k in range(askelia):
        yk = y[:, 2 * k: 2 * k + 2]
        # Haaran hinta: -korrelaatio (pienempi on parempi).
        haara = -np.einsum("bj,suj->bsu", yk, x)
        uusi = np.full((B, TILOJA), np.inf)
        valinta = np.zeros((B, TILOJA), dtype=np.int64)
        for s in range(TILOJA):
            for u in (0, 1):
                ns = SEURAAVA[s, u]
                ehdokas = metriikka[:, s] + haara[:, s, u]
                parempi = ehdokas < uusi[:, ns]
                uusi[:, ns] = np.where(parempi, ehdokas, uusi[:, ns])
                valinta[:, ns] = np.where(parempi, s, valinta[:, ns])
        metriikka = uusi
        edeltaja[k] = valinta
    # Jäljitys taaksepäin tilasta 0; syötebitti on tilan ylin bitti.
    tila = np.zeros(B, dtype=np.int64)
    paatos = np.empty((B, askelia), dtype=np.int64)
    rivit = np.arange(B)
    for k in range(askelia - 1, -1, -1):
        paatos[:, k] = tila >> 1
        tila = edeltaja[k, rivit, tila]
    tulos: Bitit = paatos[:, : askelia - 2]
    return tulos
# @loppu viterbi


# @alku lomitus
def lomita(c: Bitit, rivit: int) -> Bitit:
    """Lohkolomitus: kirjoitetaan riveittäin, luetaan sarakkeittain."""
    B, n = c.shape
    tulos: Bitit = c.reshape(B, rivit, n // rivit).transpose(0, 2, 1)
    return tulos.reshape(B, n)


def purkulomitus(c: Reaali, rivit: int) -> Reaali:
    B, n = c.shape
    tulos: Reaali = c.reshape(B, n // rivit, rivit).transpose(0, 2, 1)
    return tulos.reshape(B, n)
# @loppu lomitus
