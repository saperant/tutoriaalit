"""Yhteisjakauma taulukkona: reunajakaumat, kovarianssi ja korrelaatio."""

from fractions import Fraction
from math import sqrt

# @alku taulukko
# X = 1, jos pyyntö osuu välimuistiin, muuten 0.
# Y = pyynnön tekemien tietokantakyselyjen määrä.
# Yhteisjakauma P(X = x, Y = y) sadasosina mitatuista pyynnöistä.
yhteis = {(1, 0): Fraction(60, 100), (1, 1): Fraction(10, 100),
          (1, 2): Fraction(0), (0, 0): Fraction(0),
          (0, 1): Fraction(20, 100), (0, 2): Fraction(10, 100)}

# Reunajakauma saadaan summaamalla toinen muuttuja pois.
px = {x: sum(p for (a, _), p in yhteis.items() if a == x) for x in (0, 1)}
py = {y: sum(p for (_, b), p in yhteis.items() if b == y)
      for y in (0, 1, 2)}
print("P(X):", {x: str(p) for x, p in px.items()})
print("P(Y):", {y: str(p) for y, p in py.items()})
riippumattomat = all(p == px[x] * py[y] for (x, y), p in yhteis.items())
print("riippumattomat (P(x, y) = P(x) P(y) kaikilla):", riippumattomat)
# @loppu taulukko

# @alku kovarianssi
ex = sum(x * p for x, p in px.items())
ey = sum(y * p for y, p in py.items())
exy = sum(x * y * p for (x, y), p in yhteis.items())
kov = exy - ex * ey
var_x = sum((x - ex) ** 2 * p for x, p in px.items())
var_y = sum((y - ey) ** 2 * p for y, p in py.items())
print(f"E[X] = {ex}, E[Y] = {ey}, E[XY] = {exy}")
print(f"Cov(X, Y) = E[XY] - E[X]E[Y] = {kov}")
print(f"korrelaatio = {float(kov) / sqrt(var_x * var_y):.3f}")
# Ehdollinen odotusarvo: kyselyjä keskimäärin, kun X tunnetaan.
for x in (1, 0):
    ehd = sum(y * p for (a, y), p in yhteis.items() if a == x) / px[x]
    print(f"E[Y | X = {x}] = {ehd} = {float(ehd):.2f}")
# @loppu kovarianssi
