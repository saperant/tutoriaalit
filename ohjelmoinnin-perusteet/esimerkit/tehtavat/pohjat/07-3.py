"""Tehtävä 07-3: Korjaa kaatuva ohjelma.

Ohjelma lukee syötteestä kilpailun tulokset, rivillä nimi ja pisteet:

    Aino 9
    Ville 6

ja tulostaa keskiarvon ja parhaan:

    Keskiarvo: 7.5
    Paras: Aino (9)

Tämä versio kaatuu, jos syötteessä on tyhjä rivi, pisteet eivät ole
kokonaisluku tai tuloksia ei ole lainkaan. Kokeile, lue
virheilmoitukset ja korjaa ohjelma:

- tyhjät rivit ohitetaan
- rivistä, jonka toinen osa ei ole kokonaisluku, tulostetaan
  esimerkiksi "Rivi 2: virheelliset pisteet 'x'" ja rivi ohitetaan
- jos kelvollisia tuloksia ei ole, tulostetaan "Ei tuloksia."

Tarkistus: python3 tarkista.py 07-3
"""

import sys

tulokset: dict[str, int] = {}
for rivi in sys.stdin:
    nimi, pisteet = rivi.split()
    tulokset[nimi] = int(pisteet)

keskiarvo = sum(tulokset.values()) / len(tulokset)
paras = max(tulokset, key=lambda nimi: tulokset[nimi])
print(f"Keskiarvo: {keskiarvo:.1f}")
print(f"Paras: {paras} ({tulokset[paras]})")
