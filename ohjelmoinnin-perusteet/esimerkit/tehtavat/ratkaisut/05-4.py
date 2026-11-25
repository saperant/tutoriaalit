"""Malliratkaisu 05-4: Lisäys muuttamatta alkuperäistä."""


def lisatty(lista: list[int], alkio: int) -> list[int]:
    """Palauttaa uuden listan, jonka lopussa on alkio."""
    return [*lista, alkio]
