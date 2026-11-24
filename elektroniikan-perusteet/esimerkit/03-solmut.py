"""Solmujännitemenetelmä matriisimuodossa NumPylla."""

import numpy as np

from spice import lopeta, simuloi, vertaa

# @alku matriisi
V1, V2 = 10.0, 5.0
R1, R2, R3, R4, R5 = 1e3, 2e3, 1e3, 2e3, 1e3
g1, g2, g3, g4, g5 = (1 / r for r in (R1, R2, R3, R4, R5))

# Kirchhoffin virtalaki kummassakin solmussa: lähtevien virtojen summa
# on nolla. Tuntemattomat ovat solmujännitteet [U_a, U_b].
#   a: (U_a - V1) g1 + U_a g2 + (U_a - U_b) g3 = 0
#   b: (U_b - U_a) g3 + (U_b - V2) g4 + U_b g5 = 0
G = np.array([[g1 + g2 + g3, -g3],
              [-g3, g3 + g4 + g5]])
lahteet = np.array([V1 * g1, V2 * g4])
U_a, U_b = np.linalg.solve(G, lahteet)
# @loppu matriisi

tulos = simuloi("03-solmut.cir")
print("Solmujännitteet:")
vertaa("U_a", tulos.arvot["v(a)"], float(U_a), "V")
vertaa("U_b", tulos.arvot["v(b)"], float(U_b), "V")
lopeta()
