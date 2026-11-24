"""RL-piirin virta kasvaa aikavakiolla tau = L / R."""

import math

from spice import lopeta, simuloi, vertaa

# @alku kasin
U, R, L = 12.0, 100.0, 10e-3
tau = L / R                               # 100 us
i_loppu = U / R                           # kela on lopulta oikosulku
i_05ms = i_loppu * (1 - math.exp(-0.5e-3 / tau))
# @loppu kasin

tulos = simuloi("04-rl.cir")
print("RL-piiri, tau = 100 us:")
vertaa("t(63 %)", tulos.arvot["t63"], tau, "s")
vertaa("i(0.5 ms)", tulos.arvot["ilop"], i_05ms, "A")
lopeta()
