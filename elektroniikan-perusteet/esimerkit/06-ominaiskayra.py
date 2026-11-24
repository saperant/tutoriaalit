"""Shockleyn yhtälön parametrit simuloidusta ominaiskäyrästä."""

import math

import numpy as np

from spice import lopeta, simuloi, vertaa

# @alku sovitus
U_T = 0.025865                 # lämpöjännite kT/q, 27 C
tulos = simuloi("06-ominaiskayra.cir")
data = tulos.data["ominaiskayra"]
u, i = data[:, 0], data[:, 1]
# Shockley: I = I_S (e^(U / (n U_T)) - 1). Kun e^(...) >> 1, ln I on
# suora: ln I = ln I_S + U / (n U_T). Sovitetaan väliltä 0,3...0,5 V,
# jossa sarjaresistanssin jännitehäviö on vielä merkityksetön.
valinta = (u >= 0.3) & (u <= 0.5)
kulma, vakio = np.polyfit(u[valinta], np.log(i[valinta]), 1)
n = 1 / (kulma * U_T)
I_S = math.exp(vakio)
# @loppu sovitus
print("Sovitetut diodiparametrit (malli: IS = 2.52 nA, N = 1.752):")
vertaa("I_S", I_S, 2.52e-9, "A", 0.02)
vertaa("n", n, 1.752, "", 0.01)
# @alku kynnys
# "Kynnysjännite" ei ole vakio: jännite kasvaa n U_T ln 10 = 104 mV
# jokaista virran kymmenkertaistumista kohden.
print(f"U(1 mA) = {tulos.arvot['u1ma']:.3f} V, "
      f"U(10 mA) = {tulos.arvot['u10ma']:.3f} V")
# @loppu kynnys
lopeta()
