"""Näytteenotto ja pito: asettumisaika puolen LSB:n tarkkuuteen."""

import math

from spice import lopeta, simuloi, vertaa

# @alku asettuminen
R_on, C_h, N = 100.0, 1e-9, 12
tau = R_on * C_h
# Kondensaattorin jännite lähestyy tuloa eksponentiaalisesti. Virheen on
# pienennyttävä alle puolen LSB:n: exp(-t/tau) < 1 / 2^(N+1).
t_asettuu = tau * math.log(2 ** (N + 1))
print(f"tau = {tau * 1e9:.0f} ns, asettuminen 12 bittiin vaatii "
      f"{t_asettuu / tau:.1f} tau = {t_asettuu * 1e9:.0f} ns")
# @loppu asettuminen

tulos = simuloi("06-naytteenotto.cir").arvot
# Raja 0,999878 V on 1 V miinus puoli 12-bittistä LSB:tä (1 V:n alueella).
vertaa("t_asettuu", tulos["t_asettuu"], t_asettuu, "s", 0.02)
print(f"pitojännite kytkimen avauduttua: {tulos['u_pito']:.4f} V")
lopeta()
