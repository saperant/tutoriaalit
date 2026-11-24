"""Bipolaaritransistori kytkimenä: kantavirran mitoitus kyllästykseen."""

from spice import lopeta, simuloi, vertaa

# @alku mitoitus
U_cc, R_kuorma = 12.0, 120.0
I_c = (U_cc - 0.2) / R_kuorma          # U_CE(sat) noin 0,2 V
beta_pakotettu = 20                    # selvästi alle h_FE:n (100...300)
I_b = I_c / beta_pakotettu
U_BE = 0.75                            # kyllästyneen transistorin U_BE
R_b = (3.3 - U_BE) / I_b
print(f"I_c = {1e3 * I_c:.0f} mA, I_b = {1e3 * I_b:.1f} mA, "
      f"R_b = {R_b:.0f} ohm -> E12: 470 ohm")
# @loppu mitoitus

tulos = simuloi("07-bjt.cir")
vertaa("I_c", tulos.arvot["@rkuorma[i]"], I_c, "A", 0.02)
vertaa("I_b", tulos.arvot["@rb[i]"], (3.3 - U_BE) / 470, "A", 0.05)
# @alku teho
U_CE = tulos.arvot["v(c)"]
print(f"U_CE = {U_CE:.3f} V, häviö transistorissa "
      f"{1e3 * U_CE * tulos.arvot['@rkuorma[i]']:.0f} mW")
# @loppu teho
lopeta()
