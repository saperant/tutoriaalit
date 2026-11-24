"""Integraattori: kanttiaallosta kolmioaalto, kulmakerroin -U/(RC)."""

from spice import lopeta, simuloi, vertaa

# @alku kasin
U, R, C, T = 1.0, 10e3, 10e-9, 1e-3
kulmakerroin = U / (R * C)              # V/s, merkki vastakkainen tuloon
huipusta_huippuun = kulmakerroin * T / 2
print(f"kulmakerroin {kulmakerroin / 1e3:.0f} V/ms, "
      f"huipusta huippuun {huipusta_huippuun:.1f} V")
# @loppu kasin

tulos = simuloi("03-integraattori.cir")
nousu = (tulos.arvot["u2"] - tulos.arvot["u1"]) / 0.3e-3
vertaa("du/dt", nousu, kulmakerroin, "V/s", 0.02)
vertaa("U_hh", tulos.arvot["ylin"] - tulos.arvot["alin"],
       huipusta_huippuun, "V", 0.02)
lopeta()
