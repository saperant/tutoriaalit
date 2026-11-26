"""LDO:n vaihevara lähtökondensaattorin sarjaresistanssin (ESR) ja
kuorman funktiona sekä kuorma-askel: malli ja SPICE."""

import math

import numpy as np
from scipy.optimize import brentq

from spice import lopeta, simuloi, vertaa

# @alku malli
U_in, U_ulos, beta = 5.0, 3.3, 10e3 / 26.4e3
GM, RA, f_p2 = 2e-3, 500e3, 500e3       # virhevahvistin
C_g = 150e-12 + 70e-12                # hilan kapasitanssi yhteensä
K, lam = 1.0, 0.01                                  # päästötransistori
C_ulos = 10e-6


def T(f: float, I_k: float, ESR: float) -> complex:
    """Silmukkavahvistus: virhevahvistin (napa hilakapasitanssista ja
    sisäinen toinen napa), päästötransistori g_m ja lähtösolmun
    impedanssi, jossa kondensaattorin ESR tuo nollan."""
    s = 2j * math.pi * f
    I_d = I_k + U_ulos / 26.4e3
    U_sd = U_in - U_ulos
    g_m = math.sqrt(2 * K * I_d * (1 + lam * U_sd))
    g_ds = lam * I_d / (1 + lam * U_sd)
    Z = 1 / (g_ds + 1 / 26.4e3 + 1 / (ESR + 1 / (s * C_ulos)))
    A = GM * RA / ((1 + s * RA * C_g) * (1 + s / (2 * math.pi * f_p2)))
    return beta * A * g_m * Z


def vaihevara(I_k: float, ESR: float) -> tuple[float, float]:
    """Ylitystaajuus ja vaihevara asteina."""
    f_c = brentq(lambda f: abs(T(f, I_k, ESR)) - 1, 100, 1e8)
    f = np.logspace(0, math.log10(f_c), 400)
    vaihe = np.unwrap(np.angle([T(x, I_k, ESR) for x in f]))[-1]
    return f_c, 180 + math.degrees(vaihe)
# @loppu malli


ESR_T = (0.01, 0.5, 10.0)
tulos = simuloi("08-vakaus.cir").sarjat
print("silmukka 100 mA:n kuormalla:")
for i, ESR in enumerate(ESR_T):
    f_c, vara = vaihevara(0.1, ESR)
    print(f"ESR = {ESR:g} ohm:")
    vertaa("ylitys", tulos["fc"][i], f_c, "Hz", 0.03)
    # Vaihevara verrataan asteina, koska se voi olla lähellä nollaa.
    ero = abs(180 + tulos["vaihe"][i] - vara)
    print(f"  vaihevara    simuloitu {180 + tulos['vaihe'][i]:5.1f} deg"
          f"   laskettu {vara:5.1f} deg   {'ok' if ero < 2 else 'EROAA'}")
    if ero >= 2:
        raise SystemExit("vaihevara eroaa")
# @alku taulukko
print("vaihevara (deg) mallista:  ESR 0.01   0.1   0.5     1    10 ohm")
for I_k in (1e-3, 10e-3, 100e-3):
    varat = [vaihevara(I_k, ESR)[1] for ESR in (0.01, 0.1, 0.5, 1.0, 10.0)]
    print(f"  kuorma {I_k * 1e3:3.0f} mA           "
          + " ".join(f"{int(round(v)):5d}" for v in varat))
# @loppu taulukko
print("kuorma-askel 10 mA -> 100 mA:")
for i, ESR in enumerate(ESR_T):
    notko = tulos["alku"][i] - tulos["pohja"][i]
    heilunta = tulos["loppu_max"][i] - tulos["loppu_min"][i]
    if heilunta > 0.05:         # ei asetu: jatkuva värähtely
        print(f"  ESR = {ESR:g} ohm: värähtelee, huipusta huippuun "
              f"{heilunta:.1f} V")
    else:
        print(f"  ESR = {ESR:g} ohm: notkahdus {notko * 1e3:.0f} mV, "
              "asettuu")
vertaa("ESR-askel", tulos["alku"][1] - tulos["pohja"][1], 0.09 * 0.5, "V",
       0.03)
lopeta()
