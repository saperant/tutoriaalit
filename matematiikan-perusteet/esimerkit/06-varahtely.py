"""Harmoninen värähtely: kahden saman taajuuden siniaallon summa."""

import math

import numpy as np
import sympy as sp

# @alku summa
# 3 sin(wt) + 4 cos(wt) = R sin(wt + phi)
A, B = 3.0, 4.0
R = math.hypot(A, B)
phi = math.atan2(B, A)
print(f"R = {R:.3f}, phi = {phi:.4f} rad = {math.degrees(phi):.2f} astetta")
# @loppu summa

# @alku tarkistus
w = 2 * math.pi * 50                       # 50 Hz
t = np.linspace(0.0, 0.04, 9)
vasen = A * np.sin(w * t) + B * np.cos(w * t)
oikea = R * np.sin(w * t + phi)
print("ero alle 1e-12:", bool(np.max(np.abs(vasen - oikea)) < 1e-12))
tt = sp.symbols("t", real=True)
symbolinen = sp.expand_trig(5 * sp.sin(tt + sp.atan2(4, 3)))
print("symbolisesti:", sp.simplify(symbolinen))
# @loppu tarkistus

# @alku jakso
print(f"jaksonaika T = 1/f = {1000 / 50:.0f} ms, kulmataajuus {w:.2f} rad/s")
print(f"vaihe-ero aikana: {phi / w * 1000:.3f} ms")
# @loppu jakso
