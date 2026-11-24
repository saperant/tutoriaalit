"""Pikaoppaan tarkistukset: tärkeimmät kaavat koodilla."""

from itertools import combinations, permutations, product
from math import comb, factorial, gcd, perm

# @alku kaavat
n, k = 7, 3
assert perm(n, k) == len(list(permutations(range(n), k)))     # n!/(n-k)!
assert comb(n, k) == len(list(combinations(range(n), k)))     # n!/(k!(n-k)!)
assert len(list(product(range(n), repeat=k))) == n**k          # toisto
assert sum(comb(n, i) for i in range(n + 1)) == 2**n
assert factorial(n) == perm(n, n)
assert gcd(1071, 462) == 21 and pow(3, -1, 26) == 9
assert pow(5, 1_000_000_006, 1_000_000_007) == 1               # Fermat
print("kaavat OK")
# @loppu kaavat
