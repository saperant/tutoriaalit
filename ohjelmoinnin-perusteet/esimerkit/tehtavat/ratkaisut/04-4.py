"""Malliratkaisu 04-4: Numeroiden summa rekursiolla."""


def numeroiden_summa(luku: int) -> int:
    """Palauttaa luvun numeroiden summan."""
    if luku < 10:
        return luku
    return luku % 10 + numeroiden_summa(luku // 10)
