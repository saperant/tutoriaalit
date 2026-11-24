"""Pätö-, lois- ja näennäisteho sekä tehokerroin kompleksiluvuilla."""

import cmath
import math

from spice import lopeta, simuloi, vertaa

# @alku teho
U_eff, f = 230.0, 50.0
Z = 40 + 1j * 2 * math.pi * f * 95.5e-3       # R + j omega L
I_eff = U_eff / abs(Z)
S = U_eff * I_eff                             # näennäisteho (VA)
fii = cmath.phase(Z)                          # virran ja jännitteen vaihe-ero
P = S * math.cos(fii)                         # pätöteho (W)
Q = S * math.sin(fii)                         # loisteho (var)
print(f"|Z| = {abs(Z):.1f} ohm, vaihe-ero {math.degrees(fii):.1f} astetta")
print(f"S = {S:.0f} VA, P = {P:.0f} W, Q = {Q:.0f} var, "
      f"tehokerroin {math.cos(fii):.2f}")
# @loppu teho

tulos = simuloi("05-loisteho.cir")
vertaa("P", tulos.arvot["p"], P, "W")
vertaa("I_eff", tulos.arvot["ieff"], I_eff, "A")
lopeta()
