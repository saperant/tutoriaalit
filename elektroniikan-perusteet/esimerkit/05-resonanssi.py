"""Sarjaresonanssi: resonanssitaajuus, hyvyysluku ja kaistanleveys."""

import math

from spice import lopeta, simuloi, vertaa

# @alku kasin
L, C, R = 1e-3, 10e-9, 50.0
f0 = 1 / (2 * math.pi * math.sqrt(L * C))   # X_L = X_C
Q = math.sqrt(L / C) / R                    # hyvyysluku
kaista = f0 / Q                             # -3 dB:n kaistanleveys
# @loppu kasin

tulos = simuloi("05-resonanssi.cir")
print(f"Sarja-RLC, Q = {Q:.1f}:")
vertaa("f0", tulos.arvot["f0"], f0, "Hz")
vertaa("kaista", tulos.arvot["kaista"], kaista, "Hz")
lopeta()
