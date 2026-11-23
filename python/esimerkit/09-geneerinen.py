"""Geneeriset funktiot ja luokat (Python 3.12:n syntaksi)."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any, Protocol


# @alku funktio
def ryhmittele[K, V](alkiot: Iterable[V],
                     avain: Callable[[V], K]) -> dict[K, list[V]]:
    tulos: dict[K, list[V]] = {}
    for alkio in alkiot:
        tulos.setdefault(avain(alkio), []).append(alkio)
    return tulos


print(ryhmittele(["kissa", "koira", "hevonen", "kana"], len))
# @loppu funktio


# @alku rajattu
class Vertailtava(Protocol):
    """Kaikki tyypit, joilla on <-operaattori."""

    def __lt__(self, toinen: Any, /) -> bool: ...


def suurimmat[T: Vertailtava](alkiot: Iterable[T], n: int) -> list[T]:
    return sorted(alkiot, reverse=True)[:n]


print(suurimmat([3, 17, 5, 11], 2), suurimmat(["b", "a", "c"], 1))
# @loppu rajattu


# @alku luokka
type Tapahtuma = tuple[str, int]        # tyyppialias (3.12)


@dataclass
class Jono[T]:
    alkiot: list[T] = field(default_factory=list)

    def lisaa(self, alkio: T) -> None:
        self.alkiot.append(alkio)

    def ota(self) -> T | None:
        return self.alkiot.pop(0) if self.alkiot else None


jono: Jono[Tapahtuma] = Jono()
jono.lisaa(("kirjautuminen", 1))
print(jono.ota(), jono.ota())
# @loppu luokka
