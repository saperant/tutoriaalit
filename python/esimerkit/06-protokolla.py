"""Iteraattoriprotokolla: mitä for-silmukka tekee."""

from collections.abc import Iterator


# @alku luokka
class Sivutus:
    """Käy läpi sivunumerot; jokainen for-silmukka saa oman tilansa."""

    def __init__(self, alkioita: int, sivukoko: int) -> None:
        self.sivuja = -(-alkioita // sivukoko)    # pyöristys ylöspäin

    def __iter__(self) -> Iterator[int]:
        return iter(range(1, self.sivuja + 1))
# @loppu luokka


# @alku kertakaytto
sivut = Sivutus(alkioita=45, sivukoko=20)
print(list(sivut), list(sivut))       # iteroitava: uusi iteraattori

iteraattori = iter([1, 2, 3])
print(next(iteraattori), list(iteraattori), list(iteraattori))
# @loppu kertakaytto
