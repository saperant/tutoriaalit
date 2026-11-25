"""Differentiaalipari: erovahvistus, yhteismuotoinen vahvistus ja CMRR."""

import math

from spice import lopeta, simuloi, vertaa

# @alku kasin
U_T, BETA, V_A = 25.865e-3, 106.0, 74.0       # 27 °C; beta ja V_A mallista
U_EE, U_BE, R_c, R_ee = 12.0, 0.65, 10e3, 10e3
# Emitterisolmu on U_BE:n verran tulojen alapuolella, joten häntävirta
# on (U_EE - U_BE) / R_ee, ja se jakautuu tasan transistorien kesken.
i_hanta = (U_EE - U_BE) / R_ee
i_c = i_hanta / 2 * BETA / (BETA + 1)
g_m = i_c / U_T
r_o = V_A / i_c
# Erotulo: emitterisolmu pysyy paikallaan, ja kumpikin transistori on
# yhteisemitterivahvistin, joka saa puolet erojännitteestä.
a_d = g_m * (R_c * r_o / (R_c + r_o)) / 2
# Yhteismuotoinen tulo: molempien emitterivirta kulkee R_ee:n läpi, joka
# näkyy kummallekin transistorille kaksinkertaisena.
a_cm = BETA / (BETA + 1) * R_c / (2 * R_ee + 1 / g_m)
# @loppu kasin

tulos = simuloi("02-eropari.cir").arvot
vertaa("I_C", tulos["@q2[ic]"], i_c, "A", 0.02)
vertaa("A_d", tulos["ad_a"], a_d, "", 0.02)
vertaa("A_cm", tulos["acm_a"], a_cm, "", 0.02)
# @alku cmrr
for nimi, a_ero, a_yht in (("vastus", tulos["ad_a"], tulos["acm_a"]),
                           ("virtalähde", tulos["ad_b"], tulos["acm_b"])):
    print(f"häntänä {nimi}: A_d {a_ero:.1f}, A_cm {a_yht:.4f}, "
          f"CMRR {20 * math.log10(a_ero / a_yht):.0f} dB")
# @loppu cmrr
lopeta()
