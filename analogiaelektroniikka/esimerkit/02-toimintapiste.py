"""Bipolaaritransistorin toimintapiste: Theveninin vastine kannalle."""

from spice import lopeta, simuloi, vertaa

# @alku kasin
U_cc, R1, R2, R_c, R_e = 12.0, 47e3, 10e3, 4.7e3, 1e3
beta, U_be = 100, 0.67               # beta tällä virralla, ks. teksti
U_th = U_cc * R2 / (R1 + R2)          # kannan jakajan Thevenin-jännite
R_th = R1 * R2 / (R1 + R2)            # ja -resistanssi
I_b = (U_th - U_be) / (R_th + (beta + 1) * R_e)
I_c = beta * I_b
U_ce = U_cc - I_c * R_c - (I_c + I_b) * R_e
print(f"U_th = {U_th:.3f} V, R_th = {R_th / 1e3:.2f} kohm")
print(f"I_c = {I_c * 1e3:.3f} mA, U_CE = {U_ce:.2f} V")
# @loppu kasin

tulos = simuloi("02-toimintapiste.cir")
vertaa("I_c", tulos.arvot["@q1[ic]"], I_c, "A", 0.03)
U_ce_sim = tulos.arvot["v(c)"] - tulos.arvot["v(e)"]
vertaa("U_CE", U_ce_sim, U_ce, "V", 0.03)
# @alku tarkistus
# Toimintapiste on keskellä aktiivista aluetta, jos U_CE on selvästi
# yli kyllästysjännitteen ja alle syöttöjännitteen.
print("aktiivinen alue:", "kyllä" if 1.0 < U_ce_sim < U_cc - 1.0 else "ei")
# @loppu tarkistus
lopeta()
