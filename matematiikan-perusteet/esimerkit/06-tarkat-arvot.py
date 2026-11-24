"""Yksikköympyrä: tarkat arvot, radiaanit ja liukulukujen virhe."""

import math

import sympy as sp

# @alku tarkat
for asteet in [0, 30, 45, 60, 90, 120, 180]:
    kulma = sp.rad(asteet)
    print(f"{asteet:4d} astetta = {str(kulma):6s} rad: "
          f"sin {str(sp.sin(kulma)):9s} cos {sp.cos(kulma)}")
# @loppu tarkat

# @alku liukuluku
print("math.sin(math.pi) =", math.sin(math.pi))
print("sp.sin(sp.pi) =", sp.sin(sp.pi))
print("math.cos(math.radians(60)) =", math.cos(math.radians(60)))
print("väärä yksikkö math.sin(30) =", round(math.sin(30), 4))
# @loppu liukuluku
