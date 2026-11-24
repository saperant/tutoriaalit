"""Muistiviittausjäljet: uudelleenkäyttöetäisyys, hutikäyrät, työjoukko.

Jälkitiedoston rivi on "R osoite" tai "W osoite", osoite heksana. Jäljen
tuottaa esimerkki 02-kuormat.
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

AARETON = -1
"""Etäisyys ensimmäiselle viittaukselle riviin (pakkohuti)."""


@dataclass(frozen=True)
class Viittaus:
    kirjoitus: bool
    osoite: int


def lue_jalki(polku: Path) -> list[Viittaus]:
    """Lukee jälkitiedoston. Virheellinen rivi on ValueError."""
    jalki = []
    for n, rivi in enumerate(polku.read_text("ascii").splitlines(), 1):
        osat = rivi.split()
        if len(osat) != 2 or osat[0] not in ("R", "W"):
            raise ValueError(f"{polku}:{n}: virheellinen rivi {rivi!r}")
        jalki.append(Viittaus(osat[0] == "W", int(osat[1], 16)))
    return jalki


def rivit(jalki: Iterable[Viittaus], rivikoko: int = 64) -> list[int]:
    """Muuntaa tavuosoitteet välimuistirivien numeroiksi."""
    return [v.osoite // rivikoko for v in jalki]


# @alku mattson
def etaisyydet_pino(rivit: Sequence[int]) -> list[int]:
    """Mattsonin pinoalgoritmi (1970): LRU-pino, jonka päällä on
    viimeksi käytetty rivi. Rivin syvyys pinossa on sen
    uudelleenkäyttöetäisyys. Aika O(N * D), missä D on pinon syvyys."""
    pino: list[int] = []
    tulos = []
    for r in rivit:
        try:
            syvyys = pino.index(r)
        except ValueError:
            tulos.append(AARETON)
            pino.insert(0, r)
            continue
        tulos.append(syvyys)
        del pino[syvyys]
        pino.insert(0, r)
    return tulos
# @loppu mattson


# @alku fenwick
class _Fenwick:
    """Binääri-indeksoitu puu: pistepäivitys ja etuliitesumma O(log N)."""

    def __init__(self, koko: int) -> None:
        self._puu = [0] * (koko + 1)

    def lisaa(self, i: int, arvo: int) -> None:
        i += 1
        while i < len(self._puu):
            self._puu[i] += arvo
            i += i & -i

    def summa(self, i: int) -> int:
        """Alkioiden 0..i-1 summa."""
        s = 0
        while i > 0:
            s += self._puu[i]
            i -= i & -i
        return s


def etaisyydet(rivit: Sequence[int]) -> list[int]:
    """Sama tulos kuin etaisyydet_pino, mutta ajassa O(N log N).

    Jokaisen rivin viimeisimmän viittauksen hetkellä on puussa merkki.
    Etäisyys on merkkien määrä edellisen ja nykyisen viittauksen
    välissä, eli välissä käytettyjen eri rivien määrä."""
    puu = _Fenwick(len(rivit))
    viimeksi: dict[int, int] = {}
    tulos = []
    for t, r in enumerate(rivit):
        s = viimeksi.get(r)
        if s is None:
            tulos.append(AARETON)
        else:
            tulos.append(puu.summa(t) - puu.summa(s + 1))
            puu.lisaa(s, -1)
        puu.lisaa(t, 1)
        viimeksi[r] = t
    return tulos
# @loppu fenwick


# @alku hutikayra
def hutikayra(etaisyydet: Sequence[int], koot: Iterable[int]
              ) -> dict[int, int]:
    """Täysin assosiatiivisen LRU-välimuistin hutien määrä kullekin
    koolle (riveinä). Viittaus osuu, jos sen etäisyys on pienempi kuin
    välimuistin koko: yksi läpikäynti riittää kaikille koille."""
    jakauma: dict[int, int] = {}
    for d in etaisyydet:
        jakauma[d] = jakauma.get(d, 0) + 1
    tulos = {}
    for koko in koot:
        osumat = sum(n for d, n in jakauma.items() if 0 <= d < koko)
        tulos[koko] = len(etaisyydet) - osumat
    return tulos
# @loppu hutikayra


# @alku lru
def lru_hudit(rivit: Sequence[int], koko: int, tiet: int) -> int:
    """Suora simulointi: joukkoassosiatiivinen LRU-välimuisti, jossa on
    koko riviä ja tiet riviä joukossa (tiet == koko: täysin
    assosiatiivinen). Palauttaa hutien määrän."""
    if koko % tiet != 0:
        raise ValueError("koon on oltava teiden monikerta")
    joukot: list[list[int]] = [[] for _ in range(koko // tiet)]
    hudit = 0
    for r in rivit:
        joukko = joukot[r % len(joukot)]
        if r in joukko:
            joukko.remove(r)
        else:
            hudit += 1
            if len(joukko) == tiet:
                joukko.pop()
        joukko.insert(0, r)
    return hudit
# @loppu lru


# @alku tyojoukko
def tyojoukko(rivit: Sequence[int], ikkuna: int) -> float:
    """Denningin työjoukko: eri rivien keskimääräinen määrä ikkunoissa,
    joissa on ikkuna peräkkäistä viittausta (ikkunat eivät limity)."""
    maarat = [len(set(rivit[i:i + ikkuna]))
              for i in range(0, len(rivit) - ikkuna + 1, ikkuna)]
    if not maarat:
        raise ValueError("jälki on lyhyempi kuin ikkuna")
    return sum(maarat) / len(maarat)
# @loppu tyojoukko


# @alku laskurit
@dataclass(frozen=True)
class Laskurit:
    """Ytimen dynaamiset operaatiot luokittain (02-kuormat)."""
    lataukset: int
    tallennukset: int
    liukuluku: int
    kokonaisluku: int
    haarat: int

    @property
    def yhteensa(self) -> int:
        return (self.lataukset + self.tallennukset + self.liukuluku
                + self.kokonaisluku + self.haarat)


def lue_laskurit(polku: Path) -> dict[str, Laskurit]:
    """Lukee tiedoston, jonka rivi on "ydin lat tal liuku kok haarat"."""
    tulos = {}
    for rivi in polku.read_text("ascii").splitlines():
        nimi, *luvut = rivi.split()
        tulos[nimi] = Laskurit(*(int(x) for x in luvut))
    return tulos
# @loppu laskurit
