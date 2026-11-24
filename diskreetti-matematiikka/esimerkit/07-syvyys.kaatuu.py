"""Rekursiosyvyys on rajallinen: Python pysäyttää syvän rekursion."""


# @alku syvyys
def summa(n: int) -> int:
    """Rekursiivinen 1 + 2 + ... + n: syvyys kasvaa lineaarisesti."""
    return 0 if n == 0 else n + summa(n - 1)


print(summa(500))          # toimii
print(summa(100_000))      # RecursionError: oletusraja on noin 1000
# @loppu syvyys
