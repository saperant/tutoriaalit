"""Lokeroperiaate ja inkluusio–ekskluusio tarkistettuina."""

from itertools import permutations
from math import factorial

# @alku lokero
# n + 1 avainta n lokeroon: jokin lokero saa vähintään kaksi. Yleisesti
# jokin lokero saa vähintään ⌈avaimet / lokerot⌉ avainta.
avaimia, lokeroita = 1000, 64
print(f"{avaimia} avainta, {lokeroita} lokeroa: jossakin vähintään",
      -(-avaimia // lokeroita))
# Häviötön pakkaus ei voi lyhentää kaikkia tiedostoja: n-bittisiä
# tiedostoja on 2^n, lyhyempiä yhteensä vain 2^n - 1.
n = 16
print(f"{n}-bittisiä: {2**n}, lyhyempiä: {sum(2**k for k in range(n))}")
# @loppu lokero

# @alku inkluusio
# Kuinka moni luvuista 1…1000 on jaollinen luvulla 2, 3 tai 5?
N = 1000
kaava = (N // 2 + N // 3 + N // 5
         - N // 6 - N // 10 - N // 15
         + N // 30)
luetellen = sum(1 for x in range(1, N + 1)
                if x % 2 == 0 or x % 3 == 0 or x % 5 == 0)
print(f"jaollisia 2:lla, 3:lla tai 5:llä: kaava {kaava},",
      f"luetellen {luetellen}")
# @loppu inkluusio


# @alku epajarjestys
# Epäjärjestykset: permutaatiot, joissa kukaan ei saa omaa
# lahjaansa takaisin. Inkluusio–ekskluusio antaa
# D(n) = n! Σ (-1)^k / k!, ja D(n)/n! lähestyy arvoa 1/e ≈ 0,368.
def epajarjestykset(n: int) -> int:
    return sum((-1)**k * factorial(n) // factorial(k) for k in range(n + 1))


for n in range(1, 9):
    luettelo = sum(1 for p in permutations(range(n))
                   if all(p[i] != i for i in range(n)))
    print(f"D({n}) = {epajarjestykset(n):>5} (luetellen {luettelo:>5}),",
          f"osuus {epajarjestykset(n) / factorial(n):.4f}")
# @loppu epajarjestys
