"""Viitenumeron laskennan yksikkötestit (putken commit-vaihe)."""

import pytest
from viite.laskenta import kelpaa, muodosta, ryhmittele, tarkiste


@pytest.mark.parametrize(("runko", "odotettu"), [
    ("123456", 1),        # 7*6 + 3*5 + 1*4 + 7*3 + 3*2 + 1*1 = 89
    ("123", 2),           # 7*3 + 3*2 + 1*1 = 28
    ("1000", 3),          # 7*0 + 3*0 + 1*0 + 7*1 = 7
    ("19", None),         # liian lyhyt
])
def test_tarkiste(runko: str, odotettu: int | None) -> None:
    if odotettu is None:
        with pytest.raises(ValueError):
            tarkiste(runko)
    else:
        assert tarkiste(runko) == odotettu


def test_summa_tasan_kymmenen_antaa_nollan() -> None:
    # 7*0 + 3*0 + 1*1 + 7*7 = 50, joten tarkiste on 0 eikä 10.
    assert tarkiste("7100") == 0


def test_muodosta_ja_kelpaa_ovat_toistensa_vastinparit() -> None:
    for runko in ("123456", "100", "9999999999999999999"):
        assert kelpaa(muodosta(runko))


def test_yhden_numeron_muutos_huomataan() -> None:
    viite = muodosta("123456")
    vaara = viite[:2] + str((int(viite[2]) + 1) % 10) + viite[3:]
    assert not kelpaa(vaara)


def test_kelpaa_hyvaksyy_valilyonnit_ja_hylkaa_roskan() -> None:
    assert kelpaa("12 34561")
    assert not kelpaa("12a4561")
    assert not kelpaa("")


def test_ryhmittely_oikealta() -> None:
    assert ryhmittele("1234561") == "12 34561"
    assert ryhmittele("12345") == "12345"
