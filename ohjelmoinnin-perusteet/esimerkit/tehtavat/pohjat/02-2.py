"""Tehtävä 02-2: Matka-aika.

Ohjelma lukee matkan pituuden kilometreinä (desimaaliluku, jossa voi
olla desimaalipilkku) ja keskinopeuden (km/h, kokonaisluku). Se
tulostaa matka-ajan tunteina ja minuutteina. Minuutit pyöristetään
lähimpään kokonaiseen: round(x) pyöristää luvun x kokonaisluvuksi.

Esimerkki: syötteillä 172,5 ja 80 tuloste on

    Matka-aika: 2 h 09 min

Tarkistus: python3 tarkista.py 02-2
"""

MINUUTTEJA_TUNNISSA = 60

matka_km = input()      # muunna luvuksi; muista desimaalipilkku
nopeus_kmh = int(input())
print("Matka-aika: ? h ?? min")
