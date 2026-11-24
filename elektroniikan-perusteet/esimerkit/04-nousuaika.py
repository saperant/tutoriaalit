"""I2C-väylän nousuaika: vetovastuksen ja väyläkapasitanssin RC."""

import math

from spice import lopeta, muotoile, simuloi, vertaa

# @alku kasin
R_p, C_b = 4.7e3, 200e-12
# Jännite u = U (1 - e^(-t/RC)) saavuttaa osuuden k hetkellä
# t = -RC ln(1 - k). I2C mittaa nousuajan 30 %:sta 70 %:iin, joten
# t_r = t(70 %) - t(30 %) = RC (ln 0.7 - ln 0.3) = 0.847 RC.
t_r = R_p * C_b * math.log(0.7 / 0.3)
# @loppu kasin

tulos = simuloi("04-nousuaika.cir")
print("I2C-väylä, Rp = 4,7 kohm, Cb = 200 pF:")
vertaa("t_r", tulos.arvot["tr"], t_r, "s")

# @alku mitoitus
# Standardinopeudella (100 kbit/s) nousuaika saa olla enintään 1000 ns,
# nopeassa tilassa (400 kbit/s) 300 ns. Suurin sallittu Rp:
for tila, raja in (("100 kbit/s", 1000e-9), ("400 kbit/s", 300e-9)):
    R_max = raja / (C_b * math.log(0.7 / 0.3))
    print(f"  {tila}: Rp enintään {muotoile(R_max, 'ohm')}")
# @loppu mitoitus
lopeta()
