"""Pieni LSM-puu (log-structured merge tree) opetukseen.

Kirjoitukset menevät ensin lokiin ja muistissa olevaan memtableen.
Kun memtable täyttyy, se kirjoitetaan levylle järjestettynä,
muuttumattomana SSTable-tiedostona. Lukija etsii avainta uusimmasta
vanhimpaan: memtable, sitten SSTablet. Bloom-suodatin kertoo
halvalla, ettei avainta varmasti ole tiedostossa. Kompaktointi
yhdistää tiedostot ja poistaa vanhat versiot ja hautakivet.

Samat periaatteet ovat Cassandran, ScyllaDB:n, RocksDB:n ja LevelDB:n
tallennuskerroksessa; tämä toteutus jättää pois rinnakkaisuuden,
pakkauksen ja tasot.
"""

from __future__ import annotations

import bisect
import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

HAUTAKIVI = None  # poistettu arvo


# @alku bloom
class Bloom:
    """Bloom-suodatin: k tiivistettä bittitaulukkoon."""

    def __init__(self, bitteja: int, tiivisteita: int) -> None:
        self.bitteja = bitteja
        self.tiivisteita = tiivisteita
        self.bitit = bytearray((bitteja + 7) // 8)

    def _paikat(self, avain: str) -> list[int]:
        tiiviste = hashlib.blake2b(avain.encode(), digest_size=16).digest()
        a = int.from_bytes(tiiviste[:8], "little")
        b = int.from_bytes(tiiviste[8:], "little")
        return [(a + i * b) % self.bitteja for i in range(self.tiivisteita)]

    def lisaa(self, avain: str) -> None:
        for p in self._paikat(avain):
            self.bitit[p // 8] |= 1 << (p % 8)

    def ehka(self, avain: str) -> bool:
        """False: ei varmasti. True: ehkä (väärä positiivinen mahdollinen)."""
        return all(self.bitit[p // 8] >> (p % 8) & 1
                   for p in self._paikat(avain))
# @loppu bloom


@dataclass
class SSTable:
    """Levylle kirjoitettu, järjestetty ja muuttumaton taulu."""

    polku: Path
    avaimet: list[str]
    bloom: Bloom

    @classmethod
    def kirjoita(cls, polku: Path,
                 rivit: Sequence[tuple[str, str | None]]) -> SSTable:
        bloom = Bloom(bitteja=max(64, 10 * len(rivit)), tiivisteita=7)
        for avain, _ in rivit:
            bloom.lisaa(avain)
        polku.write_text("\n".join(json.dumps(r) for r in rivit), "utf-8")
        return cls(polku, [a for a, _ in rivit], bloom)

    def rivit(self) -> list[tuple[str, str | None]]:
        return [(a, v) for a, v in
                (json.loads(r) for r in
                 self.polku.read_text("utf-8").splitlines())]

    def hae(self, avain: str) -> tuple[bool, str | None]:
        i = bisect.bisect_left(self.avaimet, avain)
        if i < len(self.avaimet) and self.avaimet[i] == avain:
            return True, self.rivit()[i][1]
        return False, None


@dataclass
class Tilasto:
    tavuja_kirjoitettu: int = 0      # levylle, myös kompaktoinnissa
    tavuja_kayttajalta: int = 0      # sovelluksen kirjoittamat
    tiedostoja_luettu: int = 0
    bloom_ohitti: int = 0


@dataclass
class LSM:
    hakemisto: Path
    memtable_koko: int = 4
    memtable: dict[str, str | None] = field(default_factory=dict)
    taulut: list[SSTable] = field(default_factory=list)  # vanhin ensin
    tilasto: Tilasto = field(default_factory=Tilasto)
    _numero: int = 0

    # @alku kirjoitus
    def aseta(self, avain: str, arvo: str | None) -> None:
        with open(self.hakemisto / "loki", "a", encoding="utf-8") as loki:
            loki.write(json.dumps([avain, arvo]) + "\n")  # kestävyys
        self.tilasto.tavuja_kayttajalta += len(avain) + len(arvo or "")
        self.memtable[avain] = arvo
        if len(self.memtable) >= self.memtable_koko:
            self.tyhjenna()

    def poista(self, avain: str) -> None:
        self.aseta(avain, HAUTAKIVI)   # poisto on uusi versio

    def tyhjenna(self) -> None:
        self._numero += 1
        rivit = sorted(self.memtable.items())
        taulu = SSTable.kirjoita(
            self.hakemisto / f"sst-{self._numero:04d}", rivit)
        self.tilasto.tavuja_kirjoitettu += taulu.polku.stat().st_size
        self.taulut.append(taulu)
        self.memtable.clear()
        (self.hakemisto / "loki").unlink(missing_ok=True)
    # @loppu kirjoitus

    # @alku luku
    def hae(self, avain: str) -> str | None:
        if avain in self.memtable:
            return self.memtable[avain]
        for taulu in reversed(self.taulut):        # uusin ensin
            if not taulu.bloom.ehka(avain):
                self.tilasto.bloom_ohitti += 1
                continue
            self.tilasto.tiedostoja_luettu += 1
            loytyi, arvo = taulu.hae(avain)
            if loytyi:
                return arvo                        # myös hautakivi
        return None
    # @loppu luku

    # @alku kompaktointi
    def kompaktoi(self) -> None:
        """Yhdistää kaikki taulut: uusin versio voittaa, hautakivet pois."""
        yhdistetty: dict[str, str | None] = {}
        for taulu in self.taulut:                  # vanhin ensin
            yhdistetty.update(taulu.rivit())
        elavat = sorted((a, v) for a, v in yhdistetty.items()
                        if v is not HAUTAKIVI)
        for taulu in self.taulut:
            taulu.polku.unlink()
        self._numero += 1
        uusi = SSTable.kirjoita(
            self.hakemisto / f"sst-{self._numero:04d}", elavat)
        self.tilasto.tavuja_kirjoitettu += uusi.polku.stat().st_size
        self.taulut = [uusi]
    # @loppu kompaktointi
