"""Ominaisuuspohjaiset testit: väite pätee kaikille arvoille."""

from decimal import ROUND_HALF_UP, Decimal

from hypothesis import given
from hypothesis import strategies as st
from raha import jaa_tasan, jasenna, muotoile, prosentti

summat = st.integers(min_value=0, max_value=10**9)


# @alku edestakaisin
@given(sentit=summat)
def test_jasennys_kumoaa_muotoilun(sentit: int) -> None:
    assert jasenna(muotoile(sentit)) == sentit
# @loppu edestakaisin


# @alku invariantti
@given(summa=summat, osia=st.integers(min_value=1, max_value=50))
def test_jako_sailyttaa_summan(summa: int, osia: int) -> None:
    osat = jaa_tasan(summa, osia)

    assert len(osat) == osia
    assert sum(osat) == summa
    assert max(osat) - min(osat) <= 1
# @loppu invariantti


# @alku oraakkeli
def prosentti_hitaasti(sentit: int, prosentit: int) -> int:
    """Sama laskettuna desimaaliluvuilla: hidas mutta ilmeisen oikein."""
    tarkka = Decimal(sentit) * Decimal(prosentit) / Decimal(100)
    return int(tarkka.quantize(Decimal(1), rounding=ROUND_HALF_UP))


@given(sentit=summat, prosentit=st.integers(min_value=0, max_value=100))
def test_prosentti_vastaa_hidasta_toteutusta(sentit: int,
                                             prosentit: int) -> None:
    assert prosentti(sentit, prosentit) == prosentti_hitaasti(
        sentit, prosentit)
# @loppu oraakkeli
