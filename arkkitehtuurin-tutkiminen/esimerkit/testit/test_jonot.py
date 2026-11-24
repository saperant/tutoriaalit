"""Jonomallien testit: mallit ovat johdonmukaisia keskenään, ja
simulaattori on lähellä teoriaa."""

import math

from arkki.jonot import eksponentiaalinen, mg1, mm1, mmc, mva, simuloi


def test_mmc_yhdella_palvelijalla_on_mm1() -> None:
    a, c = mm1(0.07, 0.1), mmc(0.07, 0.1, 1)
    assert math.isclose(a.viipyma, c.viipyma)


def test_mg1_eksponentiaalisella_on_mm1() -> None:
    a, g = mm1(0.08, 0.1), mg1(0.08, 10.0, 2 * 10.0**2)
    assert math.isclose(a.viipyma, g.viipyma)


# @alku mva
def test_mva_rajat() -> None:
    x, r = mva(1, 100.0, [10.0])
    assert math.isclose(r, 10.0)  # yksin: ei jonoa
    x, r = mva(200, 100.0, [10.0])
    assert math.isclose(x, 0.1, rel_tol=1e-6)  # pullonkaula täynnä
# @loppu mva


def test_simulaattori_noudattaa_littlen_lakia() -> None:
    lam = 0.05
    m = simuloi(lam, eksponentiaalinen(10.0), 1, 50_000, siemen=1)
    assert math.isclose(m.maara, lam * m.viipyma, rel_tol=0.02)
    assert math.isclose(m.viipyma, 20.0, rel_tol=0.05)
    assert math.isclose(m.kayttoaste, 0.5, rel_tol=0.05)
