"""Suotimien bittitarkat mallit: FIR, polyfaasidesimaattori, IIR-lohkot
ja CIC-desimaattori.

Mallit laskevat näytteen kerrallaan samassa järjestyksessä kuin RTL ja
käsittelevät leveyden rajaukset samoin. Tila alkaa nollasta, kuten RTL
nollauksen jälkeen.
"""

from __future__ import annotations

from collections.abc import Sequence

from malli.kiintea import kierra, ulostulo


# @alku fir
def fir(
    x: Sequence[int],
    h: Sequence[int],
    siirto: int,
    bitit: int,
    pyoristys: bool = True,
    saturaatio: bool = True,
) -> list[int]:
    """Suora FIR: y[n] = kavenna(sum h[k] x[n-k]).

    Summa lasketaan tarkasti (Pythonin kokonaisluvut), joten summaus-
    järjestyksellä ei ole väliä. RTL:ssä sama pätee, kunhan summaimet ovat
    tarpeeksi leveitä: suora, transponoitu, symmetrinen ja jaettu rakenne
    antavat siksi bitilleen saman tuloksen."""
    viive = [0] * len(h)
    y = []
    for nayte in x:
        viive = [nayte, *viive[:-1]]
        summa = sum(k * v for k, v in zip(h, viive, strict=True))
        y.append(ulostulo(summa, siirto, bitit, pyoristys, saturaatio))
    return y
    # @loppu fir


# @alku desimoi
def desimoi(
    x: Sequence[int],
    h: Sequence[int],
    m: int,
    siirto: int,
    bitit: int,
    saturaatio: bool = True,
) -> list[int]:
    """Suodatus ja desimointi suoraan määritelmästä: lasketaan jokainen
    ulostulo ja säilytetään joka m:s (indeksit 0, m, 2m, ...)."""
    return fir(x, h, siirto, bitit, saturaatio=saturaatio)[::m]
    # @loppu desimoi


# @alku biquad
def biquad(
    x: Sequence[int],
    kertoimet: tuple[int, int, int, int, int],
    murto: int,
    bitit: int,
    saturaatio: bool = True,
) -> list[int]:
    """Toisen asteen lohko suorassa muodossa I (DF1).

    acc = b0 x[n] + b1 x[n-1] + b2 x[n-2] - a1 y[n-1] - a2 y[n-2]
    y[n] = kavenna(acc)

    Takaisinkytkentä käyttää kavennettua ulostuloa, kuten RTL: jos
    ulostulo kiertää saturoinnin sijaan, virhe kiertää myös
    takaisinkytkennässä."""
    b0, b1, b2, a1, a2 = kertoimet
    x1 = x2 = y1 = y2 = 0
    y = []
    for nayte in x:
        acc = b0 * nayte + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        uusi = ulostulo(acc, murto, bitit, saturaatio=saturaatio)
        x2, x1 = x1, nayte
        y2, y1 = y1, uusi
        y.append(uusi)
    return y


def sos(
    x: Sequence[int],
    lohkot: Sequence[tuple[int, int, int, int, int]],
    murto: int,
    bitit: int,
    saturaatio: bool = True,
) -> list[int]:
    """Lohkot peräkkäin: edellisen ulostulo on seuraavan sisääntulo."""
    y = list(x)
    for kertoimet in lohkot:
        y = biquad(y, kertoimet, murto, bitit, saturaatio=saturaatio)
    return y
    # @loppu biquad


# @alku cic
def cic(
    x: Sequence[int],
    asteet: int,
    r: int,
    sisainen: int,
    ulos: int,
    kierto: bool = True,
) -> list[int]:
    """CIC-desimaattori: asteet integraattoria näytetaajuudella, desimointi
    r:llä ja asteet kampaa (erotusta) matalalla taajuudella.

    Integraattorit vuotavat yli, mutta kun kaikki laskenta kiertää
    samalla leveydellä (kierto=True), kammat kumoavat ylivuodon ja tulos
    on oikea. kierto=False laskee rajattomilla kokonaisluvuilla
    vertailua varten. Lopuksi pudotetaan alimmat bitit (katkaisu)."""

    def rajaa(arvo: int) -> int:
        return kierra(arvo, sisainen) if kierto else arvo

    integ = [0] * asteet
    kammat = [0] * asteet
    y = []
    for n, nayte in enumerate(x):
        # Integraattorit ovat rekistereitä: jokainen lisää edellisen
        # asteen *vanhan* arvon, kuten RTL:n liukuhihna.
        tulot = [nayte, *integ[:-1]]
        integ = [rajaa(i + t) for i, t in zip(integ, tulot, strict=True)]
        arvo = integ[-1]
        if n % r == r - 1:
            for i in range(asteet):
                arvo, kammat[i] = rajaa(arvo - kammat[i]), arvo
            y.append(arvo >> (sisainen - ulos))
    return y
    # @loppu cic


# @alku ylivuodot
def cic_ylivuodot(x: Sequence[int], asteet: int, sisainen: int) -> int:
    """Kuinka monesti RTL:n integraattorit kiertävät: summa ei mahdu
    sisäiseen leveyteen ja ylin bitti katoaa."""
    raja = 1 << (sisainen - 1)
    integ = [0] * asteet
    ylivuodot = 0
    for nayte in x:
        tulot = [nayte, *integ[:-1]]
        summat = [i + t for i, t in zip(integ, tulot, strict=True)]
        ylivuodot += sum(not -raja <= s < raja for s in summat)
        integ = [kierra(s, sisainen) for s in summat]
    return ylivuodot
    # @loppu ylivuodot
