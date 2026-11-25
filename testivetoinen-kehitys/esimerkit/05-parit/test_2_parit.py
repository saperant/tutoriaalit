"""Parittainen kattavuus: jokainen kahden arvon yhdistelmä kokeillaan."""

from itertools import product

import pytest
from conftest import Vahvistusfunktio
from parit import Tapaus, kaikki_parit, parittaiset, tapauksen_parit
from vahvistus import PARAMETRIT

# @alku testit
TAPAUKSET = parittaiset(PARAMETRIT)


def tunniste(tapaus: Tapaus) -> str:
    return "-".join(tapaus.values())


@pytest.mark.parametrize("tapaus", TAPAUKSET, ids=tunniste)
def test_parittaiset_yhdistelmat(vahvista: Vahvistusfunktio,
                                 tapaus: Tapaus) -> None:
    assert vahvista(**tapaus)


def test_joukko_kattaa_kaikki_parit() -> None:
    katetut = set().union(*(tapauksen_parit(t) for t in TAPAUKSET))

    assert katetut == kaikki_parit(PARAMETRIT)


def test_joukko_on_pieni() -> None:
    kaikki = len(list(product(*PARAMETRIT.values())))

    assert (kaikki, len(TAPAUKSET)) == (54, 9)
# @loppu testit
