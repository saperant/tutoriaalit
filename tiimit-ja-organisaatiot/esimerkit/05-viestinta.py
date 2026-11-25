"""Viestintäpolut: yksi iso ryhmä vastaan tiimit, joilla on rajapinnat."""

TIIMIN_KOKO = 8


# @alku polut
def parit(n: int) -> int:
    """Kuinka monta eri paria n:stä voi muodostaa."""
    return n * (n - 1) // 2


def tiimeina(vakea: int, naapureita: int) -> tuple[int, int]:
    """Polut tiimien sisällä ja tiimien väliset suhteet, kun kukin
    tiimi on tekemisissä enintään naapureita-määrän tiimin kanssa."""
    tiimeja = vakea // TIIMIN_KOKO
    sisaiset = tiimeja * parit(TIIMIN_KOKO)
    suhteet = min(parit(tiimeja), tiimeja * naapureita // 2)
    return sisaiset, suhteet
# @loppu polut


print(f"{'väkeä':>6}{'yksi ryhmä':>12}{'tiimien sisällä':>17}"
      f"{'tiimisuhteita':>15}")
for vakea in (8, 16, 32, 64, 128):
    sisaiset, suhteet = tiimeina(vakea, naapureita=3)
    print(f"{vakea:>6}{parit(vakea):>12}{sisaiset:>17}{suhteet:>15}")
