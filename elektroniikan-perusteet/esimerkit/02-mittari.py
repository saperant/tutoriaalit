"""Mittarin sisäresistanssi kuormittaa suuri-impedanssista piiriä."""

from spice import lopeta, simuloi, vertaa

# @alku kasin
R1 = R2 = 1e6
R_mittari = 10e6
ilman = 10.0 * R2 / (R1 + R2)
R_rinnan = R2 * R_mittari / (R2 + R_mittari)   # rinnankytkentä
mittaus = 10.0 * R_rinnan / (R1 + R_rinnan)
# @loppu kasin

tulos = simuloi("02-mittari.cir")
print(f"todellinen jännite ilman mittaria {ilman:.2f} V")
vertaa("mitattu", tulos.arvot["v(ulos)"], mittaus, "V")
print(f"mittausvirhe {100 * (mittaus - ilman) / ilman:.1f} %")
lopeta()
