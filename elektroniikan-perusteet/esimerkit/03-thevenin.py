"""Theveninin vastine: suoran sovitus kuormituskäyrään."""

import numpy as np

from spice import lopeta, simuloi, vertaa

# @alku kasin
# Käsin: lähteet oikosuljetaan, ja R_th on solmusta b nähty resistanssi:
# ((R1 || R2) + R3) || R4 || R5.
def rinnan(*rr: float) -> float:
    return 1 / sum(1 / r for r in rr)


R_th = rinnan(rinnan(1e3, 2e3) + 1e3, 2e3, 1e3)
U_th = 3.0962          # tyhjäkäyntijännite 03-solmut.py:stä
# @loppu kasin

# @alku sovitus
tulos = simuloi("03-thevenin.cir")
data = tulos.data["thevenin"]        # sarakkeet: kuormavirta, U_b
virta, jannite = data[:, 0], data[:, 1]
kulmakerroin, vakio = np.polyfit(virta, jannite, 1)
print("Theveninin vastine solmusta b:")
vertaa("U_th", float(vakio), U_th, "V", 0.001)
vertaa("R_th", float(-kulmakerroin), R_th, "ohm")
I_n = U_th / R_th                    # Nortonin virta: oikosulkuvirta
print(f"  Nortonin vastine: I_N = {1e3 * I_n:.3f} mA rinnan R_th:n kanssa")
lopeta()
# @loppu sovitus
