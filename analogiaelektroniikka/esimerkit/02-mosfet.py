"""MOSFET-vahvistin: toimintapiste neliölaista ja vahvistus g_m R_d."""

import math

from spice import lopeta, simuloi, vertaa

# @alku kasin
U_dd, R1, R2, R_d, R_s = 12.0, 1e6, 220e3, 10e3, 1e3
K, U_TH, lam = 2e-3, 1.0, 0.01           # mallin KP, VTO ja LAMBDA
U_g = U_dd * R2 / (R1 + R2)             # hilavirta on nolla
# Kyllästysalueella I_D = K/2 (U_GS - U_TH)^2 (1 + lambda U_DS) ja
# U_GS = U_g - I_D R_s. Ratkaistaan toisen asteen yhtälö muuttujalle
# x = U_GS - U_TH; U_DS:n vaikutus otetaan mukaan muutamalla kierroksella.
U_ds = U_dd / 2
for _ in range(5):
    K_eff = K * (1 + lam * U_ds)
    a, b, c = K_eff / 2 * R_s, 1.0, -(U_g - U_TH)
    x = (-b + math.sqrt(b**2 - 4 * a * c)) / (2 * a)
    I_d = K_eff / 2 * x**2
    U_ds = U_dd - I_d * (R_d + R_s)
g_m = 2 * I_d / x                       # = sqrt(2 K I_D)
r_o = 1 / (lam * I_d)
A = g_m * R_d * r_o / (R_d + r_o)
print(f"U_GS - U_GS(th) = {x:.3f} V, I_D = {I_d * 1e3:.3f} mA, "
      f"g_m = {g_m * 1e3:.2f} mS")
# @loppu kasin

tulos = simuloi("02-mosfet.cir").arvot
vertaa("I_D", tulos["@m1[id]"], I_d, "A", 0.03)
vertaa("|A|", tulos["vm(d)"], A, "", 0.03)
lopeta()
