"""Yhteisemitterivahvistin: vahvistus ja alaraja piensignaalimallista."""

import math

from spice import lopeta, simuloi, vertaa

tulos = simuloi("02-ce-vahvistin.cir")
I_c = tulos.arvot["@q1[ic]"]

# @alku piensignaali
U_T = 0.02585                    # terminen jännite 27 °C:ssa
beta, V_A = 106, 74.0            # beta toimintapisteessä, Early-jännite
g_m = I_c / U_T                  # transkonduktanssi
r_pi = beta / g_m                # kanta-emitteriresistanssi
r_o = V_A / I_c                  # Early-ilmiön lähtöresistanssi


def rinn(*r: float) -> float:
    return 1 / sum(1 / x for x in r)


R_s, R1, R2, R_c, R_L, R_e, C_e = 50, 47e3, 10e3, 4.7e3, 10e3, 1e3, 100e-6
R_tulo = rinn(R1, R2, r_pi)
jako = R_tulo / (R_tulo + R_s)          # lähteen resistanssin vaikutus
A = g_m * rinn(R_c, R_L, r_o) * jako
print(f"g_m = {g_m * 1e3:.1f} mS, r_pi = {r_pi:.0f} ohm, "
      f"R_tulo = {R_tulo:.0f} ohm")
# @loppu piensignaali

# @alku alaraja
# Ohituskondensaattori näkee emitterin resistanssin: emitteristä katsottuna
# transistori on 1/g_m plus kannan resistanssi jaettuna (beta + 1).
r_emitteri = rinn(R_e, 1 / g_m + rinn(R_s, R1, R2) / (beta + 1))
f_ala = 1 / (2 * math.pi * r_emitteri * C_e)
# @loppu alaraja

vertaa("|A|", 10 ** (tulos.arvot["a_kesk"] / 20), A, "", 0.03)
vertaa("f_ala", tulos.arvot["f_ala"], f_ala, "Hz", 0.05)
print(f"ylärajataajuus (SPICE): {tulos.arvot['f_yla'] / 1e6:.1f} MHz")
lopeta()
