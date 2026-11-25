"""Tehtävä 05-4: Lisäys muuttamatta alkuperäistä.

Alla oleva funktio palauttaa oikean listan, mutta muuttaa samalla
kutsujan listaa. Korjaa se niin, että alkuperäinen lista säilyy:

    luvut = [1, 2]
    uudet = lisatty(luvut, 3)
    luvut  ->  [1, 2]
    uudet  ->  [1, 2, 3]

Tarkistus: python3 tarkista.py 05-4
"""


def lisatty(lista: list[int], alkio: int) -> list[int]:
    """Palauttaa uuden listan, jonka lopussa on alkio."""
    lista.append(alkio)
    return lista
