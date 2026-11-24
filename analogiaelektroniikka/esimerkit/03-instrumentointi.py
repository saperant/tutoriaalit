"""Instrumentointivahvistin: erovahvistus ja yhteismuotoisen jännitteen
vaimennus (CMRR), kun yksi vastus poikkeaa 0,1 %."""

import math

from spice import lopeta, simuloi, vertaa

# @alku kasin
R, R_g, U_ero, eps = 10e3, 1e3, 0.010, 0.001
G = 1 + 2 * R / R_g                     # tuloasteiden erovahvistus
# Erovahvistimen yhteismuotoinen vahvistus, kun yksi neljästä
# vastuksesta on (1 + eps)-kertainen: eps / (2 + eps).
A_cm = eps / (2 + eps)
CMRR = 20 * math.log10(G / A_cm)
print(f"G = {G:.0f}, A_cm = {A_cm:.2e}, CMRR = {CMRR:.1f} dB")
# @loppu kasin

# @alku simulointi
u = simuloi("03-instrumentointi.cir").sarjat["v(out)"]
# Ajot: sovitettu (U_cm 2,5 V ja 0 V), epäsovitettu (2,5 V ja 0 V).
vertaa("U_ulos", u[1], G * U_ero, "V", 0.001)
print(f"sovitettu: U_cm:n muutos 2,5 V siirtää lähtöä "
      f"{abs(u[0] - u[1]) * 1e6:.1f} uV")
A_cm_sim = (u[2] - u[3]) / 2.5
vertaa("A_cm", A_cm_sim, A_cm, "", 0.02)
vertaa("CMRR", 20 * math.log10(G / A_cm_sim), CMRR, "dB", 0.01)
# @loppu simulointi
lopeta()
