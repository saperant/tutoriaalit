"""Parametrisilmukka ngspicen .control-lohkossa ja tarkka vertailu."""

import math

from spice import lopeta, simuloi, vertaa


# @alku tarkka
def H(f: float, C: float) -> complex:
    """Kolmen kuormittavan RC-asteen siirtofunktio impedansseilla."""
    s = 2j * math.pi * f
    R = [1e3, 10e3, 100e3]
    Cs = [C, C / 10, C / 100]
    vahvistus, Z_kuorma = 1 + 0j, complex("inf")
    for r, c in reversed(list(zip(R, Cs, strict=True))):
        Z_c = 1 / (s * c)
        Z_rinnan = Z_c if math.isinf(Z_kuorma.real) else \
            Z_c * Z_kuorma / (Z_c + Z_kuorma)
        vahvistus *= Z_rinnan / (r + Z_rinnan)    # asteen jakosuhde
        Z_kuorma = r + Z_rinnan                    # edelliselle asteelle
    return vahvistus


def rajataajuus(C: float) -> float:
    ala, yla = 1.0, 1e7                 # puolitushaku logaritmisesti
    for _ in range(60):
        keski = math.sqrt(ala * yla)
        if abs(H(keski, C)) > 1 / math.sqrt(2):
            ala = keski
        else:
            yla = keski
    return keski
# @loppu tarkka


# @alku silmukka
tulos = simuloi("08-alipiiri.cir")
print("Kolmen RC-asteen ketju:")
for C, f3db in zip((10e-9, 22e-9, 47e-9), tulos.sarjat["f3db"], strict=True):
    # Ilman kuormitusta: (1 + (w tau)^2)^(-3/2) = 1/sqrt(2).
    erillinen = math.sqrt(2 ** (1 / 3) - 1) / (2 * math.pi * 1e3 * C)
    vertaa(f"C = {1e9 * C:.0f} nF", f3db, rajataajuus(C), "Hz", 0.005)
    print(f"  {'':12} kuormitusta huomioimatta {erillinen:7.0f} Hz")
lopeta()
# @loppu silmukka
