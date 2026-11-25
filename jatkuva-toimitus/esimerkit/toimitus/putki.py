"""Pieni toimitusputken ajuri.

Putki on vaiheiden riippuvuusverkko. Vaiheet, joiden edeltäjät ovat
valmiit, muodostavat aallon ja ajetaan rinnakkain. Kun vaihe
epäonnistuu, siitä riippuvia vaiheita ei ajeta: rikkinäisestä
muutoksesta ei rakenneta artefaktia.
"""

from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from graphlib import TopologicalSorter
from pathlib import Path

Toiminto = Callable[[Path], bool]


# @alku vaihe
@dataclass(frozen=True)
class Vaihe:
    nimi: str
    toiminto: Toiminto                 # palauttaa True, jos vaihe onnistui
    tarvitsee: tuple[str, ...] = ()    # vaiheet, joiden on onnistuttava


@dataclass
class Raportti:
    aallot: list[list[tuple[str, str]]] = field(default_factory=list)

    @property
    def tilat(self) -> dict[str, str]:
        return {nimi: tila for aalto in self.aallot for nimi, tila in aalto}

    @property
    def vihrea(self) -> bool:
        return all(tila == "ok" for tila in self.tilat.values())

    @property
    def ensimmainen_virhe(self) -> str | None:
        virheet = [n for n, t in self.tilat.items() if t == "VIRHE"]
        return virheet[0] if virheet else None
# @loppu vaihe


# @alku aja
def aja(vaiheet: Sequence[Vaihe], tyohak: Path) -> Raportti:
    """Ajaa vaiheet riippuvuusjärjestyksessä aalto kerrallaan."""
    nimet = {v.nimi: v for v in vaiheet}
    for v in vaiheet:
        for edeltaja in v.tarvitsee:
            if edeltaja not in nimet:
                raise ValueError(f"{v.nimi}: tuntematon vaihe {edeltaja}")
    jarjestaja = TopologicalSorter({v.nimi: v.tarvitsee for v in vaiheet})
    jarjestaja.prepare()               # CycleError, jos verkossa on kehä
    raportti = Raportti()
    tilat: dict[str, str] = {}
    while jarjestaja.is_active():
        aalto = sorted(jarjestaja.get_ready())
        ajettavat = [n for n in aalto
                     if all(tilat[e] == "ok" for e in nimet[n].tarvitsee)]
        with ThreadPoolExecutor() as saikeet:
            tulokset = saikeet.map(lambda n: nimet[n].toiminto(tyohak),
                                   ajettavat)
            onnistui = dict(zip(ajettavat, tulokset, strict=True))
        for nimi in aalto:
            if nimi not in onnistui:
                tilat[nimi] = "ohitettu"
            else:
                tilat[nimi] = "ok" if onnistui[nimi] else "VIRHE"
            jarjestaja.done(nimi)
        raportti.aallot.append([(n, tilat[n]) for n in aalto])
    return raportti
# @loppu aja


def tulosta(raportti: Raportti) -> None:
    """Tulostaa raportin: yksi rivi aaltoa kohden ja lopuksi yhteenveto."""
    for nro, aalto in enumerate(raportti.aallot, 1):
        osat = ", ".join(f"{nimi} {tila}" for nimi, tila in aalto)
        print(f"  aalto {nro}: {osat}")
    if raportti.vihrea:
        print("  putki: vihreä")
    else:
        print(f"  putki: punainen, ensimmäinen virhe vaiheessa "
              f"{raportti.ensimmainen_virhe}")
