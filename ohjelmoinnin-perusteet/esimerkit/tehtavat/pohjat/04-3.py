"""Tehtävä 04-3: Postimaksu.

Kuvitteellisen lähettipalvelun hinnasto (hinnat sentteinä):

    enintään 50 g      250
    enintään 250 g     500
    enintään 1000 g    750
    yli 1000 g        1200

Pikalähetys maksaa 300 senttiä lisää. Parametrin pikana oletusarvo
on False.

    postimaksu(50)                ->  250
    postimaksu(51)                ->  500
    postimaksu(20, pikana=True)   ->  550

Tarkistus: python3 tarkista.py 04-3
"""

PIKALISA_SNT = 300


def postimaksu(paino_g: int) -> int:
    """Palauttaa lähetyksen hinnan sentteinä."""
    return 0        # korvaa tämä rivi ja lisää parametri pikana
