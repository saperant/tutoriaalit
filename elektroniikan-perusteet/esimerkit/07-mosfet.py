"""MOSFET-kytkimen jännite- ja tehohäviö hilajännitteen funktiona."""

import numpy as np

from spice import lopeta, simuloi, vertaa

# @alku malli
K, U_T, LAMBDA = 10.0, 1.6, 0.01     # mallin KP (W = L) ja VTO


def i_d(u_gs: float, u_ds: float) -> float:
    """Tason 1 MOSFET-malli (Shichman-Hodges)."""
    u_ov = u_gs - U_T                  # ylijännite kynnyksen yli
    if u_ov <= 0:
        return 0.0
    if u_ds < u_ov:                    # lineaarinen alue: vastus
        return K * (u_ov * u_ds - u_ds**2 / 2) * (1 + LAMBDA * u_ds)
    return K / 2 * u_ov**2 * (1 + LAMBDA * u_ds)   # kyllästysalue


def u_ds(u_gs: float) -> float:
    """Toimintapiste puolitushaulla: kuorman ja transistorin virta samat."""
    ala, yla = 0.0, 12.0
    for _ in range(60):
        keski = (ala + yla) / 2
        if i_d(u_gs, keski) > (12 - keski) / 6:
            yla = keski
        else:
            ala = keski
    return (ala + yla) / 2
# @loppu malli


data = simuloi("07-mosfet.cir").data["mosfet"]
for u_gs in (2.0, 2.5, 3.3, 5.0):
    rivi = data[np.argmin(np.abs(data[:, 0] - u_gs))]
    print(f"U_GS = {u_gs:.1f} V:")
    vertaa("U_DS", float(rivi[1]), u_ds(u_gs), "V", 0.01)
    # @alku haviot
    virta = float(rivi[3])
    print(f"  I_D = {virta:.2f} A, häviö {float(rivi[1]) * virta:.2f} W")
    # @loppu haviot
lopeta()
