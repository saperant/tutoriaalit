"""Sallen-Key-alipäästö: mitoitus ja vertailu siirtofunktioon."""

import math

import numpy as np

from spice import lopeta, simuloi, vertaa

# @alku mitoitus
f_c, Q, C2 = 1e3, 1 / math.sqrt(2), 10e-9
# Yksikkövahvistuksella ja samoilla vastuksilla: Q = sqrt(C1/C2) / 2,
# joten C1 = 4 Q^2 C2, ja w0 = 1 / (R sqrt(C1 C2)).
C1 = 4 * Q**2 * C2
R = 1 / (2 * math.pi * f_c * math.sqrt(C1 * C2))
print(f"C1 = {C1 * 1e9:.0f} nF, C2 = {C2 * 1e9:.0f} nF, R = {R:.0f} ohm")
# @loppu mitoitus

# @alku siirtofunktio
# H(s) = 1 / (R^2 C1 C2 s^2 + 2 R C2 s + 1), arvo kohdassa s = j 2 pi f
nimittaja = [R**2 * C1 * C2, 2 * R * C2, 1]
f = np.array([100.0, 1e3, 10e3])
h = 1 / np.polyval(nimittaja, 2j * math.pi * f)
malli = np.abs(h)
# @loppu siirtofunktio

tulos = simuloi("04-sallen-key.cir").arvot
vertaa("f_c", tulos["f3"], f_c, "Hz", 0.01)
# Vahvistus vertaillaan lineaarisena: desibeleinä 100 Hz:n -0,0005 dB
# olisi suhteellisesti herkkä, vaikka ero on merkityksetön.
for taajuus, nimi, h_malli in zip(f, ("g100", "g1k", "g10k"), malli,
                                  strict=True):
    vertaa(f"|H| {taajuus:.0f} Hz", 10 ** (tulos[nimi] / 20),
           float(h_malli), "", 0.01)
vertaa("vaihe 1 kHz", math.degrees(tulos["v1k"]),
       math.degrees(float(np.angle(h[1]))), "deg", 0.01)
lopeta()
