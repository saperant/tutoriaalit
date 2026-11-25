"""Malliratkaisu 10-1: Testit karkausvuodelle."""

import pytest

from karkausvuosi import on_karkausvuosi


@pytest.mark.parametrize("vuosi", [2024, 2028, 1996])
def test_neljalla_jaollinen_on_karkausvuosi(vuosi: int) -> None:
    assert on_karkausvuosi(vuosi)


@pytest.mark.parametrize("vuosi", [2023, 2025, 2026])
def test_tavallinen_vuosi_ei_ole(vuosi: int) -> None:
    assert not on_karkausvuosi(vuosi)


@pytest.mark.parametrize("vuosi", [1900, 2100])
def test_sadalla_jaollinen_ei_ole(vuosi: int) -> None:
    assert not on_karkausvuosi(vuosi)


@pytest.mark.parametrize("vuosi", [1600, 2000])
def test_neljallasadalla_jaollinen_on(vuosi: int) -> None:
    assert on_karkausvuosi(vuosi)
