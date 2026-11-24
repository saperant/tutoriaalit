"""Emitteriseuraaja: vahvistus ja lähtöresistanssi kuormitusmittauksella."""

from spice import lopeta, simuloi, vertaa

tulos = simuloi("02-seuraaja.cir")
I_c = tulos.arvot["@q1[ic]"]
A_tyhja, A_kuorma = tulos.sarjat["vm(out)"]


def rinn(*r: float) -> float:
    return 1 / sum(1 / x for x in r)


# @alku kasin
beta, U_T = 106, 0.02585
R_s, R1, R2, R_e = 1e3, 22e3, 27e3, 2.2e3
r_e = U_T / I_c                                  # 1 / g_m
R_tulo = rinn(R1, R2, (beta + 1) * (r_e + R_e))  # emitterin vastus
A = R_tulo / (R_tulo + R_s) * R_e / (R_e + r_e)  # kerrottuna (beta + 1)
R_ulos = rinn(R_e, r_e + rinn(R_s, R1, R2) / (beta + 1))
print(f"r_e = {r_e:.1f} ohm, R_tulo = {R_tulo / 1e3:.1f} kohm")
# @loppu kasin

# @alku mittaus
# Kuormitettu lähtö on jännitteenjakaja: A_kuorma = A_tyhja * R_L /
# (R_L + R_ulos), josta ratkaistaan R_ulos.
R_L = 100.0
R_ulos_sim = R_L * (A_tyhja / A_kuorma - 1)
# @loppu mittaus
vertaa("A", A_tyhja, A, "", 0.02)
vertaa("R_ulos", R_ulos_sim, R_ulos, "ohm", 0.1)
lopeta()
