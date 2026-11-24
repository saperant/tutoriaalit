"""RDS-tyyppinen datakanava: lohkot, tarkistesanat ja asemanimi.

Rakenne noudattaa RDS-standardin (IEC 62106) ryhmaa 0A: nelja 26
bitin lohkoa, joissa 16 tietobittia ja 10 bitin tarkiste. Tarkiste
lasketaan polynomilla g(x) ja siihen lisataan lohkon paikan kertova
siirtymasana, jolla vastaanotin tahdistuu lohkoihin. Virheenkorjaus
jatetaan pois: vastaanotin vain tunnistaa virheelliset lohkot.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

# @alku koodi
G = 0b10110111001               # x^10 + x^8 + x^7 + x^5 + x^4 + x^3 + 1
SIIRTYMAT = {"A": 0x0FC, "B": 0x198, "C": 0x168, "D": 0x1B4}
JARJESTYS = "ABCD"


def jaannos(sana: int, bitteja: int) -> int:
    """Polynomin sana(x) jakojaannos g(x):lla (bitteja = asteluku + 1)."""
    for i in range(bitteja - 1, 9, -1):
        if sana >> i & 1:
            sana ^= G << (i - 10)
    return sana & 0x3FF


def lohko(tieto: int, paikka: str) -> int:
    """16 tietobittia -> 26 bitin lohko: tieto, tarkiste xor siirtyma."""
    if not 0 <= tieto < 1 << 16:
        raise ValueError("tietosanan on oltava 16-bittinen")
    tarkiste = jaannos(tieto << 10, 26) ^ SIIRTYMAT[paikka]
    return tieto << 10 | tarkiste


def syndrooma(sana26: int) -> int:
    """Ehjan lohkon jakojaannos on sen paikan siirtymasana."""
    return jaannos(sana26, 26)
# @loppu koodi


# @alku ryhma
def ryhma_0a(pi: int, pty: int, nimi: str, osa: int) -> list[int]:
    """Ryhma 0A: lohko B kertoo tyypin ja osoitteen, D kaksi merkkia."""
    merkit = nimi.ljust(8)[2 * osa: 2 * osa + 2].encode("ascii")
    b = 0 << 12 | 0 << 11 | 0 << 10 | pty << 5 | osa
    c = 0xE1CD                   # vaihtoehtoiset taajuudet (ei kayteta)
    d = merkit[0] << 8 | merkit[1]
    return [lohko(pi, "A"), lohko(b, "B"), lohko(c, "C"), lohko(d, "D")]


def bitit(lohkot: Iterable[int]) -> list[int]:
    """Lohkot bittijonoksi eniten merkitseva bitti ensin."""
    return [s >> i & 1 for s in lohkot for i in range(25, -1, -1)]
# @loppu ryhma


@dataclass
class Tulos:
    """Purkamisen tulos: tunniste, asemanimi ja lohkotilasto."""

    pi: int | None = None
    nimi: list[str] = field(default_factory=lambda: ["?"] * 8)
    ehjat: int = 0
    virheelliset: int = 0

    @property
    def asemanimi(self) -> str:
        return "".join(self.nimi)


# @alku pura
def pura(b: Sequence[int]) -> Tulos:
    """Etsii lohkorajan syndroomasta ja purkaa ryhmat 0A."""
    def sana(alku: int) -> int:
        arvo = 0
        for bitti in b[alku:alku + 26]:
            arvo = arvo << 1 | bitti
        return arvo

    tulos = Tulos()
    # Tahdistus: kohta, jossa kaksi perakkaista lohkoa on A ja B.
    alku = next((i for i in range(len(b) - 52)
                 if syndrooma(sana(i)) == SIIRTYMAT["A"]
                 and syndrooma(sana(i + 26)) == SIIRTYMAT["B"]), None)
    if alku is None:
        return tulos
    for i in range(alku, len(b) - 103, 104):
        ryhma = [sana(i + 26 * k) for k in range(4)]
        ehjat = [syndrooma(s) == SIIRTYMAT[p]
                 for s, p in zip(ryhma, JARJESTYS, strict=True)]
        tulos.ehjat += sum(ehjat)
        tulos.virheelliset += 4 - sum(ehjat)
        a, bb, _, d = (s >> 10 for s in ryhma)
        if ehjat[0]:
            tulos.pi = a
        if ehjat[1] and ehjat[3] and bb >> 12 == 0:
            osa = bb & 3
            tulos.nimi[2 * osa] = chr(d >> 8)
            tulos.nimi[2 * osa + 1] = chr(d & 0xFF)
    return tulos
# @loppu pura
