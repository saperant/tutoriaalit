"""Ensimmäinen analogiapiiri: invertoiva vahvistin käsin ja ngspicellä."""

from spice import lopeta, simuloi, vertaa

# @alku kasin
U_in, R1, R2, A_ol = 0.1, 10e3, 100e3, 1e5
ideaali = -R2 / R1 * U_in
# Äärellinen avoimen silmukan vahvistus: takaisinkytkentäkerroin
# beta = R1 / (R1 + R2), ja suljetun silmukan vahvistus jää hieman alle
# ideaalin, 1 / (1 + 1 / (A_ol * beta)).
beta = R1 / (R1 + R2)
todellinen = ideaali / (1 + 1 / (A_ol * beta))
print(f"ideaali {ideaali:.4f} V, äärellisellä A_ol:lla {todellinen:.5f} V")
# @loppu kasin

# @alku simulointi
tulos = simuloi("01-vahvistin.cir")
vertaa("U_ulos", tulos.arvot["v(out)"], todellinen, "V", 1e-4)
# Virtuaalimaa: tulojen välinen jännite on U_ulos / A_ol.
vertaa("U_tulo-", tulos.arvot["v(inn)"], -todellinen / A_ol, "V", 0.01)
# @loppu simulointi
lopeta()
