"""Esimerkkien kertoimet kokonaislukuina.

Kertoimet on suunniteltu SciPyllä ja kvantisoitu (ks. analyysit/
suunnittelu.py, joka tarkistaa, että suunnittelu tuottaa yhä samat
luvut). Ne kirjoitetaan tähän kokonaislukuina, jotta malli ja RTL eivät
riipu SciPyn versiosta: kertoimet ovat suunnitelman osa, eivät
käännöksen sivutuote. Työkalu malli/generoi.py kirjoittaa samat luvut
RTL:n otsaketiedostoon rtl/kertoimet.svh.
"""

from __future__ import annotations

import math

# @alku muodot
DATA_BITIT = 12  # suotimien näytteet Q1.11
KERROIN_BITIT = 16  # FIR-kertoimet Q1.15
KERROIN_MURTO = 15
# @loppu muodot

# @alku fir
# signal.firwin(8, 0.5): alipäästö, rajataajuus fs/4, Hamming-ikkuna.
FIR = [-169, -750, 3170, 14133, 14133, 3170, -750, -169]
# @loppu fir

# signal.firwin(16, 0.25): neljällä desimoivan suotimen alipäästö.
POLYFAASI = [
    -42, -177, -406, -352, 669, 2961, 5846, 7885,
    7885, 5846, 2961, 669, -352, -406, -177, -42,
]  # fmt: skip

# @alku sos
# signal.butter(4, 0.1, output="sos"), kertoimet Q2.14. Vahvistus on
# jaettu lohkoille niin, että kummankin tasavirtavahvistus on 1.
IIR_BITIT = 16  # IIR-suotimen näytteet Q1.15
IIR_MURTO = 14
SOS = [
    # b0, b1, b2, a1, a2
    (312, 624, 312, -24243, 9107),
    (359, 717, 359, -27869, 12919),
]
# @loppu sos

# @alku cordic
CORDIC_KIERROKSET = 16
CORDIC_XW = 20  # x ja y Q3.17
CORDIC_ZW = 18  # kulma: täysi kierros = 2**18


def cordic_kulmat(kierrokset: int = CORDIC_KIERROKSET) -> list[int]:
    """atan(2**-i) täyden kierroksen osina, ZW bitin tarkkuudella."""
    return [
        math.floor(
            math.atan(2.0**-i) / (2 * math.pi) * (1 << CORDIC_ZW) + 0.5
        )
        for i in range(kierrokset)
    ]


def cordic_vahvistus(kierrokset: int = CORDIC_KIERROKSET) -> float:
    """CORDICin vahvistus K = prod sqrt(1 + 2**(-2i))."""
    k = 1.0
    for i in range(kierrokset):
        k *= math.sqrt(1 + 2.0 ** (-2 * i))
    return k


# Aloituspiste 1/K muodossa Q3.17, jolloin tulos on suoraan cos ja sin.
CORDIC_X0 = math.floor((1 << 17) / cordic_vahvistus() + 0.5)
# @loppu cordic

# @alku nco
NCO_VAIHE = 24  # vaiheakkumulaattorin leveys
NCO_OSOITE = 8  # neljännesjakson taulukon osoitebitit (256 riviä)
NCO_BITIT = 12  # ulostulo Q1.11


def nco_taulukko(
    osoite: int = NCO_OSOITE, bitit: int = NCO_BITIT
) -> list[int]:
    """Neljännesjakson siniarvot puolen askeleen siirrolla.

    Puolen askeleen siirto tekee taulukosta symmetrisen: neljänneksen
    peilaus on pelkkä osoitteen bittien kääntö, eikä nollaa tai
    huippua tarvitse käsitellä erikseen."""
    n = 1 << osoite
    a = (1 << (bitit - 1)) - 1
    return [
        math.floor(a * math.sin(math.pi / 2 * (i + 0.5) / n) + 0.5)
        for i in range(n)
    ]
    # @loppu nco


# @alku cic
CIC_ASTEET = 3  # N: integraattoreita ja kampoja
CIC_DESIMOINTI = 8  # R
CIC_SISAAN = 12
CIC_SISAINEN = CIC_SISAAN + CIC_ASTEET * 3  # Bin + N log2(R M) = 21
CIC_ULOS = 16
# @loppu cic
