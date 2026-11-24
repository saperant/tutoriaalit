"""Superpositio: lineaarisen piirin vaste on lähteiden vasteiden summa."""

from spice import HAKEMISTO, lopeta, simuloi, vertaa

# @alku superpositio
piiri = (HAKEMISTO / "03-solmut.cir").read_text("utf-8")


def vaste(v1: float, v2: float) -> float:
    """Solmun b jännite, kun lähteiden arvot korvataan annetuilla."""
    teksti = (piiri.replace("V1 v1 0 DC 10", f"V1 v1 0 DC {v1}")
                   .replace("V2 v2 0 DC 5", f"V2 v2 0 DC {v2}"))
    return simuloi(teksti).arvot["v(b)"]


vain_v1 = vaste(10, 0)     # V2 oikosuljettu (0 V)
vain_v2 = vaste(0, 5)      # V1 oikosuljettu
molemmat = vaste(10, 5)
print(f"V1 yksin {vain_v1:.4f} V, V2 yksin {vain_v2:.4f} V")
vertaa("summa", vain_v1 + vain_v2, molemmat, "V", 1e-6)
# Lineaarisuus: kaksinkertainen lähde, kaksinkertainen vaste.
vertaa("2 x V1", vaste(20, 0), 2 * vain_v1, "V", 1e-6)
lopeta()
# @loppu superpositio
