"""Pieni toiminnallisen kattavuuden malli.

Kattavuuspiste jakaa havaitun arvon lokeroihin (bins), ja
ristikattavuus seuraa kahden pisteen lokeroiden yhdistelmiä. Laiton
lokero on tilanne, jota ei saa koskaan tapahtua: osuma siihen on virhe.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable
from dataclasses import dataclass, field


# @alku piste
@dataclass
class Kattavuuspiste:
    nimi: str
    lokerot: dict[str, Callable[[int], bool]]
    laittomat: dict[str, Callable[[int], bool]] = field(default_factory=dict)
    osumat: dict[str, int] = field(default_factory=dict)

    def havaitse(self, arvo: int) -> str | None:
        """Kirjaa arvon ensimmäiseen sopivaan lokeroon."""
        for nimi, ehto in self.laittomat.items():
            if ehto(arvo):
                raise AssertionError(f"{self.nimi}: laiton {nimi} ({arvo})")
        for nimi, ehto in self.lokerot.items():
            if ehto(arvo):
                self.osumat[nimi] = self.osumat.get(nimi, 0) + 1
                return nimi
        return None

    def aukot(self) -> list[str]:
        return [n for n in self.lokerot if self.osumat.get(n, 0) == 0]

    def prosentti(self) -> float:
        katettu = len(self.lokerot) - len(self.aukot())
        return 100.0 * katettu / len(self.lokerot)
        # @loppu piste


# @alku risti
@dataclass
class Ristikattavuus:
    nimi: str
    a: Kattavuuspiste
    b: Kattavuuspiste
    osumat: dict[tuple[Hashable, Hashable], int] = field(default_factory=dict)

    def havaitse(self, arvo_a: int, arvo_b: int) -> None:
        la, lb = self.a.havaitse(arvo_a), self.b.havaitse(arvo_b)
        if la is not None and lb is not None:
            self.osumat[(la, lb)] = self.osumat.get((la, lb), 0) + 1

    def aukot(self) -> list[str]:
        return [
            f"{la}*{lb}"
            for la in self.a.lokerot
            for lb in self.b.lokerot
            if self.osumat.get((la, lb), 0) == 0
        ]

    def prosentti(self) -> float:
        kaikki = len(self.a.lokerot) * len(self.b.lokerot)
        return 100.0 * (kaikki - len(self.aukot())) / kaikki
        # @loppu risti


def raportoi(pisteet: list[Kattavuuspiste | Ristikattavuus]) -> list[str]:
    """Raportti riveinä: prosentti ja kattamattomat lokerot."""
    rivit = []
    for p in pisteet:
        aukot = p.aukot()
        lisa = f" aukot: {', '.join(aukot)}" if aukot else ""
        rivit.append(f"{p.nimi:<22} {p.prosentti():5.1f} %{lisa}")
    return rivit
