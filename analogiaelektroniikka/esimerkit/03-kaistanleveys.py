"""Suljetun silmukan kaistanleveys: vahvistus-kaistanleveystulo."""

from spice import lopeta, simuloi, vertaa

# @alku kasin
GBW, A_ol, R1, R_ulos = 1e6, 1e5, 1e3, 50.0
for R2, f3 in zip((0.001, 9e3, 99e3),
                  simuloi("03-kaistanleveys.cir").sarjat["f3"], strict=True):
    G = 1 + R2 / R1                        # ihanteellinen vahvistus
    # Yksinapaisella vahvistimella suljetun silmukan napa on kohdassa
    # GBW / G. Lisäksi lähtöresistanssi ja takaisinkytkentävastukset
    # muodostavat jakajan, joka pienentää silmukkavahvistusta.
    kuorma = (R1 + R2) / (R1 + R2 + R_ulos)
    vertaa(f"G = {G:.0f}", f3, GBW * kuorma * (1 / G + 1 / A_ol), "Hz", 0.02)
# @loppu kasin
lopeta()
