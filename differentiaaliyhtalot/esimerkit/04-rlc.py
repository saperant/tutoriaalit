"""Jousi-massa-vaimennin ja sarja-RLC-piiri ovat sama yhtälö."""

import math


# @alku analogia
# m x'' + c x' + k x = F(t)  <->  L q'' + R q' + q/C = U(t)
# Ominaiskulmataajuus w0 = sqrt(k/m) = 1/sqrt(LC),
# vaimennussuhde zeta = c / (2 sqrt(km)) = (R/2) sqrt(C/L).
def mekaaninen(m: float, c: float, k: float) -> tuple[float, float]:
    return math.sqrt(k / m), c / (2 * math.sqrt(k * m))


def sahkoinen(L: float, R: float, C: float) -> tuple[float, float]:
    return 1 / math.sqrt(L * C), R / 2 * math.sqrt(C / L)


for nimi, (w0, zeta) in (
    (
        "auton jousitus m=400 kg c=4000 Ns/m k=40 kN/m",
        mekaaninen(400, 4000, 40_000),
    ),
    ("RLC L=10 mH R=20 Ohm C=1 uF", sahkoinen(10e-3, 20, 1e-6)),
    ("RLC L=10 mH R=200 Ohm C=1 uF", sahkoinen(10e-3, 200, 1e-6)),
):
    print(f"{nimi}:")
    print(f"  f0 = {w0 / (2 * math.pi):.1f} Hz, zeta = {zeta:.3f}")
# @loppu analogia
