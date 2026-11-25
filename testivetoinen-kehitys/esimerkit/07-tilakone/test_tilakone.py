"""Tilakonetesti: satunnaisia operaatiosarjoja verrataan malliin."""

from collections import Counter

import kori
import kori_viallinen
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule

tuotteet = st.sampled_from(["kahvi", "tee", "kaakao"])
maarat = st.integers(min_value=1, max_value=5)


# @alku kone
class KoriKone(RuleBasedStateMachine):
    """Kori ja yksinkertainen malli saavat samat operaatiot."""

    toteutus: type[kori.Kori] | type[kori_viallinen.Kori] = kori.Kori

    def __init__(self) -> None:
        super().__init__()
        self.kori = self.toteutus()
        self.malli: Counter[str] = Counter()

    @rule(tuote=tuotteet, maara=maarat)
    def lisaa(self, tuote: str, maara: int) -> None:
        self.kori.lisaa(tuote, maara)
        self.malli[tuote] += maara

    @rule(tuote=tuotteet, maara=maarat)
    def poista(self, tuote: str, maara: int) -> None:
        self.kori.poista(tuote, maara)
        self.malli[tuote] -= maara
        self.malli = +self.malli        # pudottaa nollat ja negatiiviset

    @invariant()
    def kori_vastaa_mallia(self) -> None:
        assert self.kori.kappaleita() == sum(self.malli.values())
        assert self.kori.riveja() == len(self.malli)
# @loppu kone


TestKori = KoriKone.TestCase


class ViallinenKone(KoriKone):
    toteutus = kori_viallinen.Kori


TestViallinenKori = ViallinenKone.TestCase
