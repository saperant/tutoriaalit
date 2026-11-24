"""Vaihevara kapasitiivisella kuormalla: malli ja SPICE-mittaus."""

import math

from scipy.optimize import brentq

from spice import lopeta, simuloi, vertaa

# @alku malli
A_ol, GBW, f_p2, R_ulos = 1e5, 10e6, 30e6, 50.0


def T(f: float, C_L: float) -> complex:
    """Seuraajan silmukkavahvistus (beta = 1): kolme napaa, joista
    kolmas syntyy lähtöresistanssista ja kuormakondensaattorista."""
    s = 2j * math.pi * f
    p1 = 2 * math.pi * GBW / A_ol
    p2 = 2 * math.pi * f_p2
    pL = 1 / (R_ulos * C_L)
    return A_ol / ((1 + s / p1) * (1 + s / p2) * (1 + s / pL))


def vaihevara(C_L: float) -> tuple[float, float]:
    """Ylitystaajuus (|T| = 1) ja vaihevara asteina."""
    f_c = brentq(lambda f: abs(T(f, C_L)) - 1, 1e3, 1e9)
    vaihe = math.degrees(sum(-math.atan(f_c / p) for p in (
        GBW / A_ol, f_p2, 1 / (2 * math.pi * R_ulos * C_L))))
    return f_c, 180 + vaihe
# @loppu malli


tulos = simuloi("05-silmukka.cir")
for C_L, f_sim, v_sim in zip((1e-12, 1e-9, 4.7e-9), tulos.sarjat["fc"],
                             tulos.sarjat["vaihe"], strict=True):
    f_c, vara = vaihevara(C_L)
    print(f"C_L = {C_L * 1e9:g} nF:")
    vertaa("ylitys", f_sim, f_c, "Hz", 0.02)
    vertaa("vaihevara", 180 + v_sim, vara, "deg", 0.03)
lopeta()
