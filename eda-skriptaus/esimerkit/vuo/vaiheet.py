"""Suunnitteluvuo vaiheina: riippuvuudet, leimat ja inkrementaalisuus."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from graphlib import TopologicalSorter
from pathlib import Path

from vuo.ajo import Ajo, aja


# @alku vaihe
@dataclass(frozen=True)
class Vaihe:
    """Vuon vaihe: komento, sen syötteet ja tulosteet.

    Syötteisiin kuuluvat myös edellisten vaiheiden tulosteet, joten
    muutos etenee vuossa eteenpäin.
    """

    nimi: str
    komento: tuple[str, ...]
    syotteet: tuple[Path, ...]
    tulosteet: tuple[Path, ...]
    riippuu: tuple[str, ...] = ()
    ymparisto: tuple[tuple[str, str], ...] = ()
# @loppu vaihe


# @alku leima
def leima(vaihe: Vaihe, versio: str) -> str:
    """Tiiviste kaikesta, mikä vaikuttaa vaiheen tulokseen."""
    h = hashlib.sha256()
    h.update(repr((vaihe.komento, vaihe.ymparisto, versio)).encode())
    for polku in sorted(vaihe.syotteet):
        h.update(str(polku).encode())
        h.update(polku.read_bytes())
    return h.hexdigest()
# @loppu leima


@dataclass
class Vuo:
    """Vaiheet riippuvuusjärjestyksessä ajohakemistossa."""

    ajohak: Path
    vaiheet: dict[str, Vaihe] = field(default_factory=dict)
    versiot: Callable[[Vaihe], str] = lambda v: ""

    def lisaa(self, vaihe: Vaihe) -> None:
        self.vaiheet[vaihe.nimi] = vaihe

    # @alku jarjestys
    def tasot(self, kohde: str | None = None) -> list[list[str]]:
        """Vaiheet tasoittain: saman tason vaiheet eivät riipu toisistaan,
        joten ne voi ajaa rinnakkain. Kohteella vain tarvittavat."""
        graafi = {n: set(v.riippuu) for n, v in self.vaiheet.items()}
        if kohde is not None:
            tarvitaan: set[str] = set()
            pino = [kohde]
            while pino:
                n = pino.pop()
                if n not in tarvitaan:
                    tarvitaan.add(n)
                    pino.extend(graafi[n])
            graafi = {n: graafi[n] for n in tarvitaan}
        lajittelija = TopologicalSorter(graafi)
        lajittelija.prepare()           # CycleError, jos riippuvuus kiertää
        tasot = []
        while lajittelija.is_active():
            taso = sorted(lajittelija.get_ready())
            tasot.append(taso)
            lajittelija.done(*taso)
        return tasot
    # @loppu jarjestys

    # @alku aja
    def aja(self, kohde: str | None = None,
            rinnakkain: int = 1) -> dict[str, str]:
        """Ajaa vanhentuneet vaiheet. Palauttaa vaiheiden tilat."""
        tilat: dict[str, str] = {}
        with ThreadPoolExecutor(rinnakkain) as pooli:
            for taso in self.tasot(kohde):
                for nimi, tila in zip(taso, pooli.map(
                        lambda n: self._aja_vaihe(n, tilat), taso),
                        strict=True):
                    tilat[nimi] = tila
        return tilat

    def _aja_vaihe(self, nimi: str, tilat: dict[str, str]) -> str:
        vaihe = self.vaiheet[nimi]
        if any(tilat[r] in ("epäonnistui", "ohitettu")
               for r in vaihe.riippuu):
            return "ohitettu"
        tiedosto = self.ajohak / "leimat" / f"{nimi}.sha256"
        uusi = leima(vaihe, self.versiot(vaihe))
        if (tiedosto.exists() and tiedosto.read_text() == uusi
                and all(p.exists() for p in vaihe.tulosteet)):
            return "ajan tasalla"
        tulos: Ajo = aja(list(vaihe.komento),
                         self.ajohak / "lokit" / f"{nimi}.log",
                         hakemisto=self.ajohak,
                         ymparisto=dict(vaihe.ymparisto))
        if not tulos.onnistui:
            tiedosto.unlink(missing_ok=True)
            return "epäonnistui"
        tiedosto.parent.mkdir(parents=True, exist_ok=True)
        tiedosto.write_text(uusi)
        return "ajettu"
    # @loppu aja
