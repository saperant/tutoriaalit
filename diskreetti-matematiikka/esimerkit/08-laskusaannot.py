"""Summa- ja tuloperiaate, permutaatiot ja kombinaatiot luetellen."""

from itertools import combinations, permutations, product
from math import comb, factorial, perm
from string import ascii_lowercase, digits

# @alku tulo
# Tuloperiaate: vaiheiden vaihtoehtomäärät kerrotaan.
pinkoodit = 10**4
kirjaimet = len(ascii_lowercase)          # 26 (ilman ääkkösiä)
merkit = kirjaimet + len(digits)          # summaperiaate: 26 + 10
print(f"PIN-koodeja: {pinkoodit}")
print(f"8 merkin salasanoja a–z0–9: {merkit**8:,}".replace(",", " "))
# Tarkistus pienellä tapauksella luettelemalla:
print("3 merkkiä 'ab01' luettelemalla:",
      len(list(product("ab01", repeat=3))), "=", 4**3)
# @loppu tulo

# @alku jarjestys
n, k = 6, 3
juoksijat = "ABCDEF"
mitalit = list(permutations(juoksijat, k))   # järjestys merkitsee
joukkueet = list(combinations(juoksijat, k))  # järjestys ei merkitse
print(f"mitalijärjestykset P({n},{k}) = {perm(n, k)},",
      f"luetellen {len(mitalit)}")
print(f"kolmen joukkueet C({n},{k}) = {comb(n, k)},",
      f"luetellen {len(joukkueet)}")
print(f"C(n,k) = P(n,k)/k!: {perm(n, k) // factorial(k) == comb(n, k)}")
# @loppu jarjestys

# @alku toisto
# Toistoja sallivat valinnat: k palloa n:stä laatikosta, järjestys ei
# merkitse ("tähdet ja väliviivat"): C(n + k - 1, k).
jaatelot = ["vanilja", "suklaa", "mansikka", "pistaasi"]
pallot = 3
annokset = {tuple(sorted(v)) for v in product(jaatelot, repeat=pallot)}
print(f"3 pallon annoksia: {len(annokset)}",
      f"= C(4 + 3 - 1, 3) = {comb(len(jaatelot) + pallot - 1, pallot)}")
# @loppu toisto
