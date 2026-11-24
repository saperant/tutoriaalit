"""Kiintopisteiteraatio x <- g(x): suppeneminen riippuu |g'(x*)|:sta."""

import math
from collections.abc import Callable


# @alku iteraatio
def iteroi(g: Callable[[float], float], x: float, n: int) -> list[float]:
    arvot = [x]
    for _ in range(n):
        x = g(x)
        arvot.append(x)
    return arvot
# @loppu iteraatio


# @alku cos
# x = cos x: |g'(x*)| = sin(x*) ~ 0.674, joten virhe pienenee joka
# kierroksella noin tällä kertoimella (lineaarinen suppeneminen).
juuri = 0.7390851332151607
arvot = iteroi(math.cos, 1.0, 30)
virheet = [abs(x - juuri) for x in arvot]
for k in (5, 10, 20, 30):
    print(f"k={k:2d}  virhe {virheet[k]:.2e}  "
          f"suhde {virheet[k] / virheet[k - 1]:.3f}")
print(f"sin(x*) = {math.sin(juuri):.3f}")
# @loppu cos

# @alku sqrt2
# Kolme tapaa kirjoittaa x^2 = 2 muotoon x = g(x).
tavat: list[tuple[str, Callable[[float], float]]] = [
    ("x = 2/x", lambda x: 2 / x),                    # g' = -1: heiluu
    ("x = x - (x^2-2)/4", lambda x: x - (x * x - 2) / 4),  # |g'| ~ 0.29
    ("x = (x + 2/x)/2", lambda x: (x + 2 / x) / 2),  # g' = 0: Newton
]
for nimi, g in tavat:
    x5 = iteroi(g, 1.0, 5)[-1]
    print(f"{nimi:18s} 5 kierrosta: {x5:.10f}  "
          f"virhe {abs(x5 - math.sqrt(2)):.1e}")
# @loppu sqrt2
