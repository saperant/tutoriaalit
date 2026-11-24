"""Jaollisuus: Eukleideen algoritmi ja Bézout'n identiteetti."""


# @alku syt
def syt(a: int, b: int, nayta: bool = False) -> int:
    """syt(a, b) = syt(b, a mod b); invariantti säilyttää yhteiset
    tekijät, ja jäännös pienenee joka kierroksella."""
    while b:
        if nayta:
            print(f"  {a} = {a // b}·{b} + {a % b}")
        a, b = b, a % b
    return a


print("syt(1071, 462) =", syt(1071, 462, nayta=True))
# @loppu syt


# @alku laajennettu
def laajennettu_syt(a: int, b: int) -> tuple[int, int, int]:
    """Palauttaa (d, x, y), joille a·x + b·y = d = syt(a, b)."""
    if b == 0:
        return a, 1, 0
    d, x, y = laajennettu_syt(b, a % b)
    return d, y, x - (a // b) * y


d, x, y = laajennettu_syt(1071, 462)
print(f"1071·({x}) + 462·{y} = {1071 * x + 462 * y} = syt")
print("tarkistus:", all(
    a * laajennettu_syt(a, b)[1] + b * laajennettu_syt(a, b)[2]
    == laajennettu_syt(a, b)[0]
    for a in range(1, 60) for b in range(1, 60)))
# @loppu laajennettu

# @alku pyj
# Pienin yhteinen jaettava: kaksi aikataulua kohtaavat pyj:n välein.
bussi, juna = 12, 18
print(f"bussi {bussi} min ja juna {juna} min lähtevät yhtä aikaa",
      f"{bussi * juna // syt(bussi, juna)} minuutin välein")
# @loppu pyj
