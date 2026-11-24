"""Ensimmäinen piiri: jännitteenjakaja simuloituna ja käsin laskettuna."""

from spice import lopeta, simuloi, vertaa

# @alku kasin
U = 12.0            # syöttöjännite (V)
R1, R2 = 10e3, 4.7e3
virta = U / (R1 + R2)  # sama virta kulkee molempien vastusten läpi
U_ulos = virta * R2
# @loppu kasin

# @alku simulointi
tulos = simuloi("01-jakaja.cir")
print("Jännitteenjakaja:")
vertaa("U_ulos", tulos.arvot["v(ulos)"], U_ulos, "V")
# Lähteen virta on SPICEssä negatiivinen: se kulkee lähteen läpi + -> -.
vertaa("I", -tulos.arvot["i(v1)"], virta, "A")
lopeta()
# @loppu simulointi
