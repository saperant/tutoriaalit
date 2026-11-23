"""Suomalaisen pankkiviitteen (viitenumeron) tarkiste ja tarkistus.

Tarkiste lasketaan kertomalla perusosan numerot oikealta alkaen
painoilla 7, 3, 1, 7, 3, 1, ... ja vähentämällä tulojen summa
seuraavasta täydestä kymmenestä. Erotus 10 tarkoittaa tarkistetta 0.
Perusosassa on 3–19 numeroa, joten koko viitteessä on 4–20 numeroa.
"""

PAINOT = (7, 3, 1)


def laske_tarkiste(perusosa: str) -> int:
    """Palauttaa perusosan tarkistenumeron."""
    if not perusosa.isdigit() or not 3 <= len(perusosa) <= 19:
        raise ValueError(f"virheellinen perusosa: '{perusosa}'")
    summa = 0
    for i, numero in enumerate(reversed(perusosa)):
        summa += int(numero) * PAINOT[i % 3]
    return (10 - summa % 10) % 10


def muodosta_viite(perusosa: str) -> str:
    """Lisää perusosaan tarkisteen."""
    return perusosa + str(laske_tarkiste(perusosa))


def on_kelvollinen(viite: str) -> bool:
    """Tarkistaa viitteen. Välilyönnit ryhmittelynä sallitaan."""
    numerot = viite.replace(" ", "")
    if not numerot.isdigit() or not 4 <= len(numerot) <= 20:
        return False
    return laske_tarkiste(numerot[:-1]) == int(numerot[-1])
