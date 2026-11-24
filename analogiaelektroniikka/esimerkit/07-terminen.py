"""Terminen kohina: vastuksen tiheys sqrt(4kTR) ja RC:n kT/C-kohina."""

import math

from spice import lopeta, simuloi, vertaa

# @alku kasin
k_B, T = 1.380649e-23, 300.15          # ngspicen oletuslämpötila 27 °C
R, C = 1e3, 1e-9
tiheys = math.sqrt(4 * k_B * T * R)    # V / sqrt(Hz)
# RC-alipäästön ekvivalentti kohinakaista on (pi / 2) f_c = 1 / (4 R C),
# joten kokonaiskohina sqrt(4kTR / (4RC)) = sqrt(kT/C): R supistuu pois.
kTC = math.sqrt(k_B * T / C)
print(f"1 kohm: {tiheys * 1e9:.2f} nV/sqrt(Hz), kT/C 1 nF: "
      f"{kTC * 1e6:.2f} uV rms")
# @loppu kasin

tulos = simuloi("07-terminen.cir")
vertaa("tiheys", tulos.arvot["onoise_spectrum[0]"], tiheys, "V/rtHz", 0.001)
for R_k, kokonais in zip(("1k", "100k"), tulos.sarjat["onoise_total"],
                         strict=True):
    vertaa(f"R = {R_k}", kokonais, kTC, "V", 0.002)
lopeta()
