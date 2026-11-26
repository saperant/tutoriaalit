"""Buck-muunnin kiinteällä pulssisuhteella: jatkuva ja katkeava
kelavirta, rippeli ja hyötysuhde."""

import math

from spice import lopeta, simuloi, vertaa

# @alku jatkuva
U_in, D, f_k = 12.0, 0.275, 200e3
L, C = 100e-6, 47e-6
T = 1 / f_k
# Jatkuva johtuminen: kelan jännitteen keskiarvo on nolla, joten
# (U_in - U) D = U (1 - D) eli U = D U_in kuormasta riippumatta.
U = D * U_in
dI = (U_in - U) * D * T / L         # kelavirran rippeli huipusta huippuun
dU = dI * T / (8 * C)               # lähdön rippeli (ihanteellinen C)
I_raja = dI / 2                     # tätä pienempi kuormavirta katkeaa
print(f"U = {U:.2f} V, kelavirran rippeli {dI * 1e3:.0f} mA, "
      f"lähdön rippeli {dU * 1e3:.2f} mV, raja {I_raja * 1e3:.0f} mA")
# @loppu jatkuva


# @alku katkeava
def katkeava(R: float) -> float:
    """Lähtö, kun kelan virta käy nollassa ennen jakson loppua. Kela
    siirtää jaksossa kiinteän energian, joten jännite riippuu kuormasta."""
    k = 2 * L / (R * T)
    return U_in * 2 / (1 + math.sqrt(1 + 4 * k / D**2))
# @loppu katkeava


# @alku haviot
R_on, R_k = 0.1, 3.3
U_T, I_s, n, R_s = 0.025865, 10e-6, 1.05, 0.02     # Schottky-diodi


def haviollinen() -> tuple[float, float]:
    """Lähtö ja hyötysuhde, kun kytkimessä on resistanssi ja diodissa
    myötäjännite. Syötöstä otetaan virtaa vain kytkimen johtaessa, joten
    syöttövirran keskiarvo on D kertaa kelavirta."""
    I_k = U / R_k
    for _ in range(20):
        U_d = n * U_T * math.log(I_k / I_s) + I_k * R_s
        I_k = (D * (U_in - I_k * R_on) - (1 - D) * U_d) / R_k
    return I_k * R_k, I_k * R_k / (D * U_in)
# @loppu haviot


t = simuloi("08-buck.cir").sarjat
print("jatkuva johtuminen, kuorma 3.3 ohm:")
vertaa("lähtö", t["uka"][0], U, "V", 0.005)
vertaa("kelan dI", t["imax"][0] - t["imin"][0], dI, "A", 0.02)
vertaa("lähdön dU", t["umax"][0] - t["umin"][0], dU, "V", 0.06)
print("katkeava johtuminen, kuorma 330 ohm:")
vertaa("lähtö", t["uka"][1], katkeava(330.0), "V", 0.01)
print(f"  kelavirran pienin arvo {max(t['imin'][1], 0.0) * 1e3:.0f} mA")
print("häviölliset osat, kuorma 3.3 ohm:")
U_h, eta = haviollinen()
P_ulos = t["uka"][2] ** 2 / R_k
vertaa("lähtö", t["uka"][2], U_h, "V", 0.005)
vertaa("hyötysuhde", P_ulos / (U_in * -t["iin"][2]), eta, "", 0.01)
print(f"  häviö {(U_in * -t['iin'][2] - P_ulos) * 1e3:.0f} mW; "
      f"lineaarisäätimessä {(U_in - U) * 1.0:.1f} W ja hyötysuhde "
      f"{U / U_in:.1%}")
lopeta()
