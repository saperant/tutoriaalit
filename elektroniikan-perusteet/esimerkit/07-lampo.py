"""Liitoslämpötila häviötehosta ja kotelon lämpöresistanssista."""

import numpy as np

from spice import simuloi

# @alku lampo
T_YMPARISTO, T_J_MAX = 40.0, 150.0          # °C: kotelon sisällä, datalehti
# Lämpöresistanssi liitoksesta ympäristöön (K/W), tyypillisiä arvoja:
KOTELOT = {"SOT-23": 250.0, "TO-220 ilman jäähdytintä": 62.0}


def liitoslampotila(teho: float, r_theta: float) -> float:
    """T_j = T_a + P * R_theta: lämpöpiirin Ohmin laki."""
    return T_YMPARISTO + teho * r_theta
# @loppu lampo


# Häviöt samasta simulaatiosta kuin esimerkissä 07-mosfet.py.
data = simuloi("07-mosfet.cir").data["mosfet"]
print("U_GS   häviö   " + "  ".join(KOTELOT))
for u_gs in (2.0, 2.5, 3.3, 5.0):
    rivi = data[np.argmin(np.abs(data[:, 0] - u_gs))]
    teho = float(rivi[1] * rivi[3])
    lammot = []
    for r_theta in KOTELOT.values():
        t_j = liitoslampotila(teho, r_theta)
        lammot.append(f"{t_j:4.0f} °C {'ok' if t_j < T_J_MAX else 'yli'}")
    print(f"{u_gs:.1f} V  {teho:4.2f} W  " + "   ".join(lammot))

# @alku jaahdytin
# Suurin sallittu lämpöresistanssi 5,87 W:n häviölle:
rivi = data[np.argmin(np.abs(data[:, 0] - 2.0))]
teho = float(rivi[1] * rivi[3])
print(f"{teho:.2f} W vaatii R_theta < "
      f"{(T_J_MAX - T_YMPARISTO) / teho:.1f} K/W")
# @loppu jaahdytin
