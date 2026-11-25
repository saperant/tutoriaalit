"""Logiikkatasot ja kohinamarginaalit CMOS-invertterin siirtokäyrästä."""

import numpy as np

from spice import lopeta, simuloi, vertaa

# @alku tasot
# Siirtokäyrä on sama DC-pyyhkäisy kuin esimerkissä 07-cmos.py.
data = simuloi("07-cmos.cir").data["cmos"]
u_in, u_out = data[:, 0], data[:, 1]
kulma = np.gradient(u_out, u_in)
# Tulon rajat ovat pisteet, joissa käyrän kulmakerroin on -1: niiden
# välissä portti vahvistaa tulon häiriöitä, ulkopuolella vaimentaa.
jyrkka = np.flatnonzero(kulma < -1.0)
u_il, u_ih = float(u_in[jyrkka[0]]), float(u_in[jyrkka[-1]])
u_oh, u_ol = float(u_out[jyrkka[0]]), float(u_out[jyrkka[-1]])
# @loppu tasot

# @alku marginaalit
# Symmetriselle invertterille (sama K ja kynnys kummallakin
# transistorilla) rajat saa suljetussa muodossa:
U_DD, U_T = 1.8, 0.45
vertaa("U_IL", u_il, (3 * U_DD + 2 * U_T) / 8, "V", 0.03)
vertaa("U_IH", u_ih, (5 * U_DD - 2 * U_T) / 8, "V", 0.03)
print(f"  U_OH = {u_oh:.2f} V, U_OL = {u_ol:.2f} V")
print(f"  kohinamarginaalit: alhaalla {1e3 * (u_il - u_ol):.0f} mV, "
      f"ylhäällä {1e3 * (u_oh - u_ih):.0f} mV")
# @loppu marginaalit

# @alku yhteensopivuus
# Taatut tasot (V): lähdön U_OH ja U_OL, tulon U_IH ja U_IL.
TASOT = {
    "3,3 V CMOS":         (2.4, 0.4, 2.0, 0.8),
    "5 V CMOS (74HC)":    (4.4, 0.1, 3.15, 1.35),
    "5 V, TTL-tasot (74HCT)": (4.4, 0.1, 2.0, 0.8),
}


def marginaalit(lahto: str, tulo: str) -> tuple[float, float]:
    """Kohinamarginaalit, kun `lahto` ohjaa tuloa `tulo`."""
    u_oh_l, u_ol_l, _, _ = TASOT[lahto]
    _, _, u_ih_t, u_il_t = TASOT[tulo]
    return u_oh_l - u_ih_t, u_il_t - u_ol_l


for lahto, tulo in (("3,3 V CMOS", "3,3 V CMOS"),
                    ("3,3 V CMOS", "5 V CMOS (74HC)"),
                    ("3,3 V CMOS", "5 V, TTL-tasot (74HCT)"),
                    ("5 V CMOS (74HC)", "3,3 V CMOS")):
    yla, ala = marginaalit(lahto, tulo)
    tila = "kelpaa" if min(yla, ala) > 0 else "EI KELPAA"
    print(f"{lahto} -> {tulo}:")
    print(f"  marginaali ylhäällä {yla:+.2f} V, "
          f"alhaalla {ala:+.2f} V: {tila}")
# @loppu yhteensopivuus
lopeta()
