"""Binomikertoimet: Pascalin kolmio, identiteetit ja hilapolut."""

from functools import cache
from itertools import combinations
from math import comb

# @alku pascal
rivi = [1]
for n in range(7):
    luvut = " ".join(f"{x:>2}" for x in rivi)
    print(f"n={n}: " + luvut.center(40).rstrip())
    rivi = [1] + [a + b for a, b in zip(rivi, rivi[1:], strict=False)] + [1]
# @loppu pascal

# @alku identiteetit
N = range(30)
print("C(n,k) = C(n,n-k):",
      all(comb(n, k) == comb(n, n - k) for n in N for k in range(n + 1)))
print("Σ_k C(n,k) = 2^n:",
      all(sum(comb(n, k) for k in range(n + 1)) == 2**n for n in N))
print("Pascal C(n,k) = C(n-1,k-1) + C(n-1,k):",
      all(comb(n, k) == comb(n - 1, k - 1) + comb(n - 1, k)
          for n in range(1, 30) for k in range(1, n)))
# Binomilause (x + y)^n = Σ C(n,k) x^k y^(n-k), tarkistettuna luvuilla.
print("binomilause:",
      all((x + y)**n == sum(comb(n, k) * x**k * y**(n - k)
                            for k in range(n + 1))
          for n in range(12) for x in range(-3, 4) for y in range(-3, 4)))
# @loppu identiteetit


# @alku hilapolut
@cache
def polkuja(oikealle: int, ylos: int) -> int:
    """Reitit ruudukossa vain oikealle ja ylös (dynaaminen ohjelmointi)."""
    if oikealle == 0 or ylos == 0:
        return 1
    return polkuja(oikealle - 1, ylos) + polkuja(oikealle, ylos - 1)


# Reitti on 10 askeleen jono, josta valitaan 4 ylös-askelta: C(10, 4).
luetellen = sum(1 for _ in combinations(range(10), 4))
print(f"6×4-ruudukko: {polkuja(6, 4)} reittiä, C(10,4) = {comb(10, 4)},",
      f"luetellen {luetellen}")
# @loppu hilapolut
