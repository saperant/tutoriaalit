"""Tehtävä 04-4: Numeroiden summa rekursiolla.

Kirjoita funktio, joka palauttaa ei-negatiivisen kokonaisluvun
numeroiden summan. Älä käytä silmukkaa: funktio kutsuu itseään.

    numeroiden_summa(472)  ->  13      (4 + 7 + 2)

Päättymisehto: yksinumeroisen luvun summa on luku itse. Muuten summa
on viimeinen numero (luku % 10) plus muiden numeroiden (luku // 10)
summa.

Tarkistus: python3 tarkista.py 04-4
"""


def numeroiden_summa(luku: int) -> int:
    """Palauttaa luvun numeroiden summan."""
    return 0        # korvaa tämä rivi
