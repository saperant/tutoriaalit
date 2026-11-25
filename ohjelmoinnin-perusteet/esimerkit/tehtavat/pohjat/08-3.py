"""Tehtävä 08-3: Varasto ja invariantti.

Kirjoita luokka Varasto. Konstruktori saa kapasiteetin. Invariantti:
varaston määrä on aina välillä 0–kapasiteetti.

    varasto = Varasto(10)
    varasto.lisaa(4)
    varasto.ota(1)
    varasto.maara     ->  3

- lisaa ja ota nostavat ValueErrorin, jos määrä ei ole positiivinen.
- Jos lisäys ylittäisi kapasiteetin tai varastosta otettaisiin
  enemmän kuin siellä on, nostetaan oma poikkeus VarastoVirhe eikä
  määrä muutu.
- maara on luettavissa mutta ei sijoitettavissa (@property).

Tarkistus: python3 tarkista.py 08-3
"""


class VarastoVirhe(Exception):
    """Varaston kapasiteetti ylittyisi tai tavaraa ei ole tarpeeksi."""


class Varasto:
    """Varasto, jonka määrä pysyy välillä 0–kapasiteetti."""
