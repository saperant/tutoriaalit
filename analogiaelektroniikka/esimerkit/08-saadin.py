"""Lineaarisäädin sisältä: tasajänniteominaisuudet kahdella
päästötransistorilla (LDO ja seuraaja)."""

import math

from scipy.optimize import brentq

from spice import lopeta, simuloi, vertaa

# @alku osat
U_ref, R1, R2 = 1.25, 16.4e3, 10e3
beta = R2 / (R1 + R2)               # takaisinkytkentäkerroin
A = 2e-3 * 500e3                    # virhevahvistin: GM * RA = 1000
U_t, lam = 1.6, 0.01                # transistorien kynnys ja lambda
K_p, K_n = 5.0 * 20 / 100, 10.0     # KP * W/L (A/V^2)
U_nim = U_ref / beta                # nimellinen lähtö 3,30 V


def ylijannite(I_d: float, K: float, U_ds: float) -> float:
    """Kyllästysalueen U_GS - U_t virralla I_d (neliölaki)."""
    return math.sqrt(2 * I_d / (K * (1 + lam * U_ds)))
# @loppu osat


# @alku toimintapiste
def ldo(U_in: float, I_k: float) -> tuple[float, float]:
    """LDO:n lähtö ja hilajännite. Vahvistin tarvitsee tulojensa välille
    eron U_g / A, joka näkyy lähdössä kerrottuna 1 / beta:lla."""
    U_ulos = U_nim
    for _ in range(5):
        I_d = I_k + U_ulos / (R1 + R2)
        U_g = U_in - U_t - ylijannite(I_d, K_p, U_in - U_ulos)
        U_ulos = (U_ref + U_g / A) / beta
    return U_ulos, U_g


def seuraaja(U_in: float, I_k: float) -> tuple[float, float]:
    """Seuraajan hila on lähdön yläpuolella, ja virhe on vastakkainen."""
    U_ulos = U_nim
    for _ in range(5):
        I_d = I_k + U_ulos / (R1 + R2)
        U_g = U_ulos + U_t + ylijannite(I_d, K_n, U_in - U_ulos)
        U_ulos = (U_ref - U_g / A) / beta
    return U_ulos, U_g
# @loppu toimintapiste


# @alku pudotus
RAJA = 0.99 * U_nim                 # lähtö pudonnut 1 %


def pudotus_ldo(I_k: float) -> float:
    """Hila on maassa ja transistori vastusalueella: pienin syöttö,
    jolla virta I_d vielä kulkee, kun lähtö on rajalla."""
    I_d = I_k + RAJA / (R1 + R2)

    def virta(U_in: float) -> float:
        U_sd = U_in - RAJA
        return K_p * ((U_in - U_t) * U_sd - U_sd**2 / 2) * (1 + lam * U_sd)

    return brentq(lambda u: virta(u) - I_d, RAJA, RAJA + 1) - RAJA


def pudotus_seuraaja(I_k: float) -> float:
    """Hila ei nouse syötön yli, joten syötön on oltava lähtöä
    kynnysjännitteen ja ylijännitteen verran korkeammalla."""
    I_d = I_k + RAJA / (R1 + R2)
    return brentq(lambda d: U_t + ylijannite(I_d, K_n, d) - d, 1.0, 3.0)
# @loppu pudotus


t = simuloi("08-saadin.cir").arvot
print(f"nimellinen lähtö {U_nim:.3f} V, vahvistus A = {A:g}, "
      f"A * beta = {A * beta:.0f}")
print("LDO (P-kanava), syöttö 5 V:")
vertaa("virhe", t["v(out)"] - U_nim, ldo(5.0, 0.1)[0] - U_nim, "V", 0.02)
vertaa("hila", t["v(g)"], ldo(5.0, 0.1)[1], "V", 0.005)
vertaa("kuorma", t["kuorma_ldo"], ldo(5.0, 0.1)[0] - ldo(5.0, 1e-3)[0],
       "V", 0.03)
vertaa("linja", t["linja_ldo"], 1 / (A * beta), "V/V", 0.03)
vertaa("pudotus", t["pud_ldo"] - RAJA, pudotus_ldo(0.1), "V", 0.03)
print("seuraaja (N-kanava), syöttö 7 V:")
vertaa("virhe", t["v(out2)"] - U_nim, seuraaja(7.0, 0.1)[0] - U_nim,
       "V", 0.02)
vertaa("hila", t["v(g2)"], seuraaja(7.0, 0.1)[1], "V", 0.005)
vertaa("kuorma", t["kuorma_seur"],
       seuraaja(7.0, 0.1)[0] - seuraaja(7.0, 1e-3)[0], "V", 0.03)
vertaa("linja", t["linja_seur"],
       seuraaja(7.5, 0.1)[0] - seuraaja(6.5, 0.1)[0], "V/V", 0.05)
vertaa("pudotus", t["pud_seur"] - RAJA, pudotus_seuraaja(0.1), "V", 0.03)
# @alku hyoty
for nimi, U_in in (("LDO, syöttö 5 V", 5.0), ("LDO, syöttö 3,6 V", 3.6),
                   ("seuraaja, syöttö 5,3 V", 5.3)):
    haviot = (U_in - U_nim) * 0.1
    print(f"{nimi}: häviö {haviot * 1e3:.0f} mW, "
          f"hyötysuhde {U_nim / U_in:.0%}")
# @loppu hyoty
lopeta()
