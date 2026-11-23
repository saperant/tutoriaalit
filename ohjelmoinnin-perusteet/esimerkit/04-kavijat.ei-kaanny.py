"""Arvo kulkee funktioon parametrina ja ulos paluuarvona."""

kavijoita = 0


def kirjaa_kavija_vaarin() -> None:          # @virhe
    kavijoita = kavijoita + 1  # paikallinen!  # @virhe


def kirjaa_kavija(kavijoita: int) -> int:
    """Palauttaa kävijämäärän yhdellä kasvatettuna."""
    return kavijoita + 1


for _ in range(3):
    kavijoita = kirjaa_kavija(kavijoita)
print(kavijoita)
