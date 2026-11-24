"""RC-alipäästö kompleksisella impedanssilla ja SPICEn AC-analyysillä."""

import cmath
import math

from spice import lopeta, simuloi, vertaa

# @alku kompleksi
R, C = 1e3, 100e-9
f_c = 1 / (2 * math.pi * R * C)               # rajataajuus


def H(f: float) -> complex:
    """Siirtofunktio jännitteenjakajana: Z_C / (R + Z_C)."""
    Z_C = 1 / (1j * 2 * math.pi * f * C)      # kondensaattorin impedanssi
    return Z_C / (R + Z_C)


def db(h: complex) -> float:
    return 20 * math.log10(abs(h))
# @loppu kompleksi


tulos = simuloi("05-alipaasto.cir")
print(f"RC-alipäästö, f_c = {f_c:.1f} Hz:")
vertaa("f(-3 dB)", tulos.arvot["f3db"], f_c, "Hz")
vertaa("10 f_c", tulos.arvot["vahv10k"], db(H(10 * f_c)), "dB")
vaihe = math.degrees(cmath.phase(H(f_c)))
vertaa("vaihe f_c", tulos.arvot["vaihe"], vaihe, "aste")
lopeta()
