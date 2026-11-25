"""Tehtävä 09-3: Modulista ohjelmaksi.

Tämä tiedosto toimii ohjelmana: se lukee leveyden ja korkeuden ja
tulostaa pinta-alan. Modulina sitä ei voi käyttää, koska tuonti
(import) suorittaa pääohjelman ja jää odottamaan syötettä.

Muuta tiedosto niin, että

- pääohjelma on funktiossa main ja se suoritetaan vain, kun tiedosto
  ajetaan ohjelmana (if __name__ == "__main__":)
- tuotaessa ei lueta syötettä eikä tulosteta mitään
- pinta_ala(3.0, 4.0) palauttaa 12.0 ja ohjelma tulostaa syötteillä
  3 ja 4 rivin "Pinta-ala: 12.0".

Tarkistus: python3 tarkista.py 09-3
"""


def pinta_ala(leveys: float, korkeus: float) -> float:
    """Palauttaa suorakulmion pinta-alan."""
    return leveys * korkeus


leveys = float(input())
korkeus = float(input())
print(f"Pinta-ala: {pinta_ala(leveys, korkeus)}")
