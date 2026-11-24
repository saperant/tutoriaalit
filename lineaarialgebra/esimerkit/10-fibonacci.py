"""Diagonalisointi: Fibonaccin luvut ominaisarvoista."""

import math

import numpy as np

# @alku matriisi
# [F(n+1), F(n)] = A [F(n), F(n-1)], missä A = [[1, 1], [1, 0]].
A = np.array([[1, 1], [1, 0]], dtype=np.int64)
print("A^10 =", np.linalg.matrix_power(A, 10).tolist(), "-> F(10) = 55")
# @loppu matriisi

# @alku diagonalisointi
# A = V D V^-1, joten A^n = V D^n V^-1: potenssi lasketaan lävistäjältä.
arvot, V = np.linalg.eigh(A.astype(float))      # symmetrinen matriisi
print("ominaisarvot:", np.round(arvot, 6).tolist())
fii = (1 + math.sqrt(5)) / 2
print(f"kultainen leikkaus φ = {fii:.6f}")


def fibonacci(n: int) -> int:
    """Binetin kaava: F(n) = (φ^n − ψ^n)/√5, missä ψ = −1/φ."""
    return round((fii ** n - (-1 / fii) ** n) / math.sqrt(5))


print("F(1..12):", [fibonacci(n) for n in range(1, 13)])
# @loppu diagonalisointi

# @alku raja
# Liukuluku riittää F(70):een asti; sen jälkeen tarvitaan kokonaislukuja.
def fibonacci_tarkka(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


eka_virhe = next(n for n in range(1, 200)
                 if fibonacci(n) != fibonacci_tarkka(n))
print("liukuluku menee väärin ensimmäisen kerran: n =", eka_virhe)
# @loppu raja
