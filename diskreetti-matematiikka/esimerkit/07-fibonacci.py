"""Fibonaccin luvut: rekursioyhtälö, kutsujen määrä ja suljettu muoto."""

from functools import cache
from math import sqrt

kutsuja = 0


# @alku naiivi
def fib_naiivi(n: int) -> int:
    """F(n) = F(n-1) + F(n-2), F(0) = 0, F(1) = 1."""
    global kutsuja
    kutsuja += 1
    if n < 2:
        return n
    return fib_naiivi(n - 1) + fib_naiivi(n - 2)
# @loppu naiivi


# @alku nopeat
@cache
def fib_muisti(n: int) -> int:
    return n if n < 2 else fib_muisti(n - 1) + fib_muisti(n - 2)


def fib_silmukka(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
# @loppu nopeat


# @alku kutsut
# Kutsujen määrä K(n) = K(n-1) + K(n-2) + 1 = 2F(n+1) - 1: kasvaa
# samaa tahtia kuin luvut itse, noin 1,618^n.
for n in (10, 20, 25):
    kutsuja = 0
    arvo = fib_naiivi(n)
    print(f"F({n}) = {arvo}, kutsuja {kutsuja}",
          f"(2F({n + 1}) - 1 = {2 * fib_silmukka(n + 1) - 1})")
# @loppu kutsut

# @alku binet
# Suljettu muoto (Binet): F(n) = (φ^n - ψ^n)/√5. Liukuluvuilla kaava
# pettää, kun luvut kasvavat yli liukuluvun tarkkuuden.
phi, psi = (1 + sqrt(5)) / 2, (1 - sqrt(5)) / 2


def fib_binet(n: int) -> int:
    return round((phi**n - psi**n) / sqrt(5))


virhe = next(n for n in range(200) if fib_binet(n) != fib_silmukka(n))
print(f"Binet'n kaava liukuluvuilla pettää ensin, kun n = {virhe}")
print("F(300) muistilla == silmukalla:", fib_muisti(300) == fib_silmukka(300))
# @loppu binet
