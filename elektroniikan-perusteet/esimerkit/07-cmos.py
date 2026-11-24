"""CMOS-invertterin kytkentäkynnys ja viiveet transistorien leveyksistä."""

import math

from spice import HAKEMISTO, lopeta, muotoile, simuloi, vertaa

piiri = (HAKEMISTO / "07-cmos.cir").read_text("utf-8")
# @alku kynnys
U_DD, U_TN, U_TP = 1.8, 0.45, 0.45
KP_N, KP_P, L = 200e-6, 80e-6, 0.18e-6


def kynnys(w_p: float, w_n: float = 1e-6) -> float:
    """Kytkentäkynnys U_M, jossa molemmat transistorit ovat
    kyllästysalueella ja niiden virrat ovat yhtä suuret."""
    r = math.sqrt((KP_P * w_p / L) / (KP_N * w_n / L))
    return (U_TN + r * (U_DD - U_TP)) / (1 + r)
# @loppu kynnys


for w_p in ("2.5u", "1u"):
    tulos = simuloi(piiri.replace(".param Wp=2.5u", f".param Wp={w_p}"))
    print(f"W_p = {w_p}m:")
    # Kanavanpituusmodulaatio (LAMBDA) siirtää kynnystä hieman.
    vertaa("U_M", tulos.arvot["vm"], kynnys(float(w_p[:-1]) * 1e-6), "V",
           0.03)
    # @alku viive
    print(f"  t_pHL {muotoile(tulos.arvot['tphl'], 's')}, "
          f"t_pLH {muotoile(tulos.arvot['tplh'], 's')}")
    # @loppu viive
lopeta()
