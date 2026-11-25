"""Tehtävä 02-3: Lasku tasan.

Ohjelma lukee laskun loppusumman sentteinä ja maksajien määrän. Se
tulostaa yhden maksajan osuuden euroina ja sen, montako senttiä jää
jakamatta, kun jokainen maksaa täsmälleen saman summan. Raha
käsitellään kokonaislukuina; liukulukuja ei tarvita.

Esimerkki: syötteillä 8650 ja 3 tuloste on

    Osuus: 28,83 €, jakamatta: 1 snt

Tarkistus: python3 tarkista.py 02-3
"""

summa_snt = int(input())
maksajia = int(input())
print("Osuus: ?,?? €, jakamatta: ? snt")
