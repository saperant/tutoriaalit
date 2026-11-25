"""Tehtävä 10-1: Testit karkausvuodelle.

Tässä tehtävässä kirjoitetaan testit, ei toteutusta. Moduli
karkausvuosi sisältää funktion on_karkausvuosi(vuosi). Kirjoita sille
pytest-testit, jotka kattavat säännön jokaisen haaran: tavallinen
vuosi, neljällä jaollinen, sadalla jaollinen ja 400:lla jaollinen.

Tarkistin ajaa testisi oikeaa toteutusta vasten (kaikkien pitää mennä
läpi) ja kolmea virheellistä toteutusta vasten (jokaisen pitää jäädä
kiinni vähintään yhteen testiin).

Tarkistus: python3 tarkista.py 10-1
Oma ajo:   python3 -m pytest 10-1.py   (hakemistossa tehtavat/omat)
"""

from karkausvuosi import on_karkausvuosi


def test_neljalla_jaollinen_on_karkausvuosi() -> None:
    assert on_karkausvuosi(2024)
