"""CORDICin ja numeerisesti ohjatun oskillaattorin bittitarkat mallit."""

from __future__ import annotations

from collections.abc import Sequence

from malli.kertoimet import (
    CORDIC_KIERROKSET,
    CORDIC_XW,
    CORDIC_ZW,
    NCO_BITIT,
    NCO_OSOITE,
    NCO_VAIHE,
    cordic_kulmat,
    nco_taulukko,
)
from malli.kiintea import kierra

ROTAATIO = 0
VEKTORI = 1


# @alku alku
def esikierto(tila: int, x: int, y: int, z: int) -> tuple[int, int, int]:
    """Sisääntulot (Q1.15 ja 16-bittinen kulma) sisäiseen muotoon.

    CORDIC suppenee vain, kun kierrettävä kulma on välillä noin
    [-99, 99] astetta. Muut tapaukset käännetään puoli kierrosta:
    vektori vaihtaa merkkiä ja kulmaan lisätään pii."""
    x, y, z = x << 2, y << 2, z << 2  # Q1.15 -> Q3.17, 16 -> 18 bittiä
    if tila == ROTAATIO:
        kaanna = ((z >> 17) ^ (z >> 16)) & 1 == 1  # 2. tai 3. neljännes
    else:
        kaanna = x < 0
    if kaanna:
        x, y, z = -x, -y, z + (1 << (CORDIC_ZW - 1))
    return x, y, kierra(z, CORDIC_ZW)
    # @loppu alku


# @alku iteraatio
def iteraatio(
    tila: int, i: int, x: int, y: int, z: int, kulma: int
) -> tuple[int, int, int]:
    """Yksi CORDIC-kierros: kierto kulmalla +-atan(2**-i) pelkillä
    siirroilla ja yhteenlaskuilla."""
    if tila == ROTAATIO:
        d = 1 if z >= 0 else -1  # kierretään kohti z = 0
    else:
        d = 1 if y < 0 else -1  # kierretään kohti y = 0
    return (
        kierra(x - d * (y >> i), CORDIC_XW),
        kierra(y + d * (x >> i), CORDIC_XW),
        kierra(z - d * kulma, CORDIC_ZW),
    )
    # @loppu iteraatio


# @alku cordic
def cordic(
    tila: int, x: int, y: int, z: int, kierrokset: int = CORDIC_KIERROKSET
) -> tuple[int, int, int]:
    """Koko CORDIC: esikierto ja kierrokset. Palauttaa sisäiset arvot
    (x ja y Q3.17, z 18-bittisenä kulmana), kuten RTL."""
    kulmat = cordic_kulmat(kierrokset)
    x, y, z = esikierto(tila, x, y, z)
    for i in range(kierrokset):
        x, y, z = iteraatio(tila, i, x, y, z, kulmat[i])
    return x, y, z
    # @loppu cordic


# @alku nco
def nco(
    taajuussana: int,
    n: int,
    vaihe: int = NCO_VAIHE,
    osoite: int = NCO_OSOITE,
    bitit: int = NCO_BITIT,
) -> list[int]:
    """n näytettä sinistä, jonka taajuus on taajuussana / 2**vaihe
    näytetaajuudesta. Vaiheesta käytetään osoite + 2 ylintä bittiä:
    kaksi valitsee neljänneksen, loput osoittavat taulukkoon."""
    taulukko = nco_taulukko(osoite, bitit)
    maski = (1 << osoite) - 1
    akku = 0
    y = []
    for _ in range(n):
        p = akku >> (vaihe - osoite - 2)  # vaiheen katkaisu
        neljannes, indeksi = p >> osoite, p & maski
        if neljannes & 1:
            indeksi = maski - indeksi  # peilaus: bittien kääntö
        arvo = taulukko[indeksi]
        y.append(-arvo if neljannes & 2 else arvo)
        akku = (akku + taajuussana) & ((1 << vaihe) - 1)
    return y
    # @loppu nco


def cordic_kaikki(
    syotteet: Sequence[tuple[int, int, int, int]],
) -> list[tuple[int, int, int]]:
    """Sama kuin cordic() jokaiselle (tila, x, y, z)-nelikolle."""
    return [cordic(*s) for s in syotteet]
