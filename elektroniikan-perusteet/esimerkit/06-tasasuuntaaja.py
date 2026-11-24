"""Kokoaaltotasasuuntaajan rippeli: kaksi arviota ja simulointi."""

import numpy as np

from spice import lopeta, muotoile, simuloi, vertaa

# @alku arvio
U_F = 0.85                            # diodin jännite suurella virralla
U_dc = 12.0 * 2**0.5 - 2 * U_F        # kaksi diodia johtaa kerrallaan
R, C, f = 100.0, 1000e-6, 50.0
# Karkea arvio: kondensaattori syöttää kuormaa koko puolijakson
# (1 / 2f) vakiovirralla, joten dU = I dt / C. Tämä on yläraja.
karkea = (U_dc / R) / (2 * f * C)
# @loppu arvio

# @alku tarkempi
# Tarkempi arvio: kondensaattori purkautuu eksponentiaalisesti huipusta,
# kunnes tasasuunnattu siniaalto nousee taas sen yli.
t = np.linspace(0, 1 / (2 * f), 100_001)
u_c = U_dc * np.exp(-t / (R * C))
u_s = U_dc * np.abs(np.cos(2 * np.pi * f * t))
lataus = np.argmax((u_s >= u_c) & (t > 1 / (8 * f)))
tarkempi = float(U_dc - u_c[lataus])
# @loppu tarkempi

tulos = simuloi("06-tasasuuntaaja.cir")
print("Diodisilta, C = 1000 uF, kuorma 100 ohm:")
vertaa("U_max", tulos.arvot["umax"], U_dc, "V", 0.05)
print(f"  karkea rippeliarvio {muotoile(karkea, 'V')}")
vertaa("rippeli", tulos.arvot["aalto"], tarkempi, "V", 0.15)
lopeta()
