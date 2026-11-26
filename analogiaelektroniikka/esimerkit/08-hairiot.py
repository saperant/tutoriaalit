"""LDO: syötön häiriöiden vaimennus (PSRR) ja lähdön kohina."""

import math

from spice import lopeta, simuloi, vertaa

# @alku psrr
U_in, U_ulos, beta, I_k = 5.0, 3.3, 10e3 / 26.4e3, 0.1
GM, RA, f_p2 = 2e-3, 500e3, 500e3
C_gs, C_ea = 150e-12, 70e-12
K, lam, C_ulos, ESR = 1.0, 0.01, 10e-6, 0.5


def psrr(f: float) -> float:
    """Syötön vaihtojännitteen vaimennus lähdössä desibeleinä.

    Avoimella silmukalla syötön muutos näkyy transistorin lähteen ja
    hilan välissä. Hila seuraa syöttöä kapasitanssin C_gs kautta, mutta
    RA ja C_ea pitävät sitä maassa. Suljettu silmukka jakaa tuloksen
    tekijällä 1 + T."""
    s = 2j * math.pi * f
    I_d = I_k + U_ulos / 26.4e3
    U_sd = U_in - U_ulos
    g_m = math.sqrt(2 * K * I_d * (1 + lam * U_sd))
    g_ds = lam * I_d / (1 + lam * U_sd)
    Z = 1 / (g_ds + 1 / 26.4e3 + 1 / (ESR + 1 / (s * C_ulos)))
    napa = 1 + s * RA * (C_gs + C_ea)
    hila = (1 + s * RA * C_ea) / napa       # u_sg / u_in
    suora = (g_m * hila + g_ds) * Z         # ilman takaisinkytkentää
    T = (beta * GM * RA / (napa * (1 + s / (2 * math.pi * f_p2)))) * g_m * Z
    return -20 * math.log10(abs(suora / (1 + T)))
# @loppu psrr


# @alku kohina
k_B, T_K = 1.380649e-23, 300.15
R_n, R_jako, R_vahv = 1e6, 16.4e3 * 10e3 / 26.4e3, 1e3


def tiheys(f: float, C_nr: float) -> float:
    """Lähdön kohinatiheys silmukan kaistalla: referenssin, jakovastusten
    ja vahvistimen tulon kohina vahvistuu kertoimella 1 / beta."""
    suodin = 1 / (1 + (2 * math.pi * f * R_n * C_nr) ** 2)
    return math.sqrt(4 * k_B * T_K
                     * (R_n * suodin + R_jako + R_vahv)) / beta
# @loppu kohina


t = simuloi("08-hairiot.cir")
print(f"A * beta = {GM * RA * beta:.0f} eli "
      f"{20 * math.log10(GM * RA * beta):.1f} dB")
vertaa("PSRR 100 Hz", t.arvot["p100"], psrr(100), "dB", 0.01)
vertaa("PSRR 10 kHz", t.arvot["p10k"], psrr(10e3), "dB", 0.01)
vertaa("PSRR 200 kHz", t.arvot["p200k"], psrr(200e3), "dB", 0.01)
for C_nr, nimi, n1k, kok in zip(
        (1e-15, 100e-9), ("ilman suodatusta", "Cnr = 100 nF"),
        t.sarjat["onoise_spectrum[40]"], t.sarjat["onoise_total"],
        strict=True):
    print(f"kohina, {nimi}:")
    vertaa("1 kHz", n1k, tiheys(1e3, C_nr), "V/rtHz", 0.02)
    print(f"  10 Hz ... 100 kHz yhteensä {kok * 1e6:.0f} uV rms")
lopeta()
