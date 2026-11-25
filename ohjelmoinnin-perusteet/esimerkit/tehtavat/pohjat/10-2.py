"""Tehtävä 10-2: Testit kellonajan jäsennykselle.

Moduli kellonaika sisältää funktion minuutteina(teksti), joka muuntaa
kellonajan "t:mm" tai "tt:mm" minuuteiksi keskiyöstä:

    minuutteina("7:05")   ->  425
    minuutteina("23:59")  ->  1439

Virheellinen kellonaika (tunnit yli 23, minuutit yli 59, kaksoispiste
puuttuu, ei numeroita) nostaa ValueErrorin.

Kirjoita testit: tunnettu tulos, rajatapaukset (0:00 ja 23:59, yksi
yli kummassakin kentässä) ja virheelliset syötteet. Tarkistin ajaa
testisi oikeaa ja neljää virheellistä toteutusta vasten.

Tarkistus: python3 tarkista.py 10-2
"""

import pytest

from kellonaika import minuutteina


def test_tunnettu_kellonaika() -> None:
    assert minuutteina("7:05") == 425


def test_kirjaimet_hylataan() -> None:
    with pytest.raises(ValueError):
        minuutteina("abc")
