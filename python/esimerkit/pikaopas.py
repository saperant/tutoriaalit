"""Pikaoppaan koodinäytteet."""

from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Protocol

# @alku perus
rivit = ["ada 3", "bob 5", "ada 4", "eve x"]
pisteet: defaultdict[str, int] = defaultdict(int)
for rivi in rivit:
    nimi, _, arvo = rivi.partition(" ")       # purku
    if arvo.isdigit():
        pisteet[nimi] += int(arvo)
parhaat = sorted(pisteet.items(), key=lambda p: p[1], reverse=True)
neliot = {n: n * n for n in range(5) if n % 2}  # dict-koostelauseke
print(parhaat, neliot, f"{3.14159:.2f}", f"{len(rivit)=}")
# @loppu perus

# @alku luokat
@dataclass(frozen=True, slots=True)
class Piste:
    x: float
    y: float

    def siirra(self, dx: float, dy: float) -> "Piste":
        return Piste(self.x + dx, self.y + dy)


@dataclass
class Reitti:
    nimi: str
    pisteet: list[Piste] = field(default_factory=list)  # ei []


class Piirtaja(Protocol):          # rakenteellinen rajapinta
    def piirra(self, p: Piste) -> str: ...


class Teksti:                      # ei perintää: muoto riittää
    def piirra(self, p: Piste) -> str:
        return f"({p.x}, {p.y})"


def piirra_kaikki(r: Reitti, piirtaja: Piirtaja) -> str:
    return " -> ".join(piirtaja.piirra(p) for p in r.pisteet)


reitti = Reitti("lenkki", [Piste(0, 0), Piste(0, 0).siirra(1, 2)])
print(piirra_kaikki(reitti, Teksti()))
# @loppu luokat

# @alku iteraattorit
def parilliset(luvut: Iterable[int]) -> Iterator[int]:
    for n in luvut:                # laiska: arvo kerrallaan
        if n % 2 == 0:
            yield n


@contextmanager
def osio(nimi: str) -> Iterator[None]:
    print(f"<{nimi}>")
    try:
        yield
    finally:                       # ajetaan myös poikkeuksessa
        print(f"</{nimi}>")


with osio("raportti"):
    print(sum(parilliset(range(10))), Counter("banaani").most_common(1))
# @loppu iteraattorit

# @alku virheet
def portti(arvo: str) -> int:
    try:
        n = int(arvo)              # EAFP: yritä, käsittele virhe
    except ValueError:
        raise ValueError(f"ei portti: {arvo!r}") from None
    if not 0 < n < 65536:
        raise ValueError(f"alueen ulkopuolella: {n}")
    return n


for ehdokas in ["8080", "http", "0"]:
    try:
        print(portti(ehdokas))
    except ValueError as virhe:
        print("virhe:", virhe)
# @loppu virheet
