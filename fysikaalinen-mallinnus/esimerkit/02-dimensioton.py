"""Dimensioton lämpöyhtälö: yksi käyrä kattaa kaikki levyt.

Levy (paksuus 2L) on aluksi tasalämpöinen, ja sen pinnat pakotetaan
hetkellä 0 uuteen lämpötilaan. Keskikohdan dimensioton lämpötila
riippuu vain Fourier'n luvusta Fo = alfa t / L²."""

import math

# @alku sarja
def keskikohta(fo: float, termeja: int = 60) -> float:
    """theta = (T - T_pinta)/(T_alku - T_pinta) levyn keskellä."""
    summa = 0.0
    for n in range(termeja):
        lam = (2 * n + 1) * math.pi / 2
        summa += 2.0 * (-1) ** n / lam * math.exp(-lam * lam * fo)
    return summa


def fo_kun(theta: float) -> float:
    """Fourier'n luku, jolla keskikohta on saavuttanut arvon theta."""
    a, b = 1e-3, 5.0                     # theta vähenee: puolitushaku
    for _ in range(60):
        c = 0.5 * (a + b)
        if keskikohta(c) > theta:
            a = c
        else:
            b = c
    return 0.5 * (a + b)
# @loppu sarja


# @alku aineet
# Lämpötilanjohtavuus alfa = k/(rho c), m²/s (suuruusluokat).
AINEET = {"kupari": 1.1e-4, "teräs": 1.2e-5, "lasi": 5.0e-7,
          "mänty": 1.5e-7}

fo_puoli = fo_kun(0.5)
fo_valmis = fo_kun(0.01)
print(f"keskikohta puolivälissä, kun Fo = {fo_puoli:.3f}; "
      f"1 % jäljellä, kun Fo = {fo_valmis:.2f}")
print("aine      paksuus  puoliväli     1 % jäljellä")
for aine, alfa in AINEET.items():
    for paksuus_mm in (10.0, 20.0):
        puolikas = paksuus_mm / 2000.0           # L metreinä
        t1 = fo_puoli * puolikas**2 / alfa
        t2 = fo_valmis * puolikas**2 / alfa
        print(f"{aine:8s} {paksuus_mm:5.0f} mm {t1:9.1f} s {t2:11.1f} s")
# @loppu aineet
