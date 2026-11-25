"""Epävakaat testit: pieni vika testiä kohden, iso vika putkea kohden.

Jokainen epävakaa testi epäonnistuu satunnaisesti pienellä
todennäköisyydellä, vaikka koodissa ei ole vikaa. Lasketaan, kuinka
usein koko putki silti menee läpi, ja mitä uudelleenajo maksaa.
"""

import random


# @alku lapi
def lapi(testeja: int, hairio: float) -> float:
    """Todennäköisyys, että yksikään epävakaa testi ei petä."""
    return (1 - hairio) ** testeja


def simuloi(testeja: int, hairio: float, ajoja: int, siemen: int) -> float:
    arpa = random.Random(siemen)
    vihreat = sum(all(arpa.random() >= hairio for _ in range(testeja))
                  for _ in range(ajoja))
    return vihreat / ajoja
# @loppu lapi


print("epävakaita testejä, kukin pettää kerran 200 ajossa (0,5 %)")
print(f"{'testejä':>8}{'laskettu':>10}{'simuloitu':>11}")
for testeja in (1, 10, 50, 100, 300):
    print(f"{testeja:>8}{lapi(testeja, 0.005):>10.1%}"
          f"{simuloi(testeja, 0.005, 4000, siemen=3):>11.1%}")

# @alku uusinta
# Uudelleenajo: testi hyväksytään, jos se menee läpi yhdelläkin
# kolmesta yrityksestä. Häiriö katoaa näkyvistä, mutta niin katoaa
# myös oikea vika, joka ilmenee vain osassa ajoista.
oikea_vika = 0.30            # kilpatilanne: epäonnistuu 30 %:ssa ajoista
print("\nkolme yritystä, yksi onnistuminen riittää")
print(f"  50 epävakaata testiä: putki läpi {lapi(50, 0.005 ** 3):.2%}")
print(f"  oikea vika, joka näkyy 30 %:ssa ajoista: "
      f"läpi {1 - oikea_vika ** 3:.0%}")
# @loppu uusinta
