"""Vektorien laskutoimitukset: summa, skaalaus, pituus ja normit."""

import math

import numpy as np

Vektori = list[float]


def muoto(v: Vektori) -> str:
    """Kaksi desimaalia; -0.00 näytetään nollana."""
    return "(" + ", ".join(f"{round(x, 2) + 0.0:.2f}" for x in v) + ")"


# @alku perus
def summa(a: Vektori, b: Vektori) -> Vektori:
    return [x + y for x, y in zip(a, b, strict=True)]


def skaalaa(k: float, v: Vektori) -> Vektori:
    return [k * x for x in v]


# Robotti ajaa kolme siirtymää (metreinä itään ja pohjoiseen).
siirtymat = [[3.0, 0.0], [0.0, 4.0], [-1.0, 1.0]]
paikka = [0.0, 0.0]
for s in siirtymat:
    paikka = summa(paikka, s)
print("loppupaikka:", muoto(paikka))
print("puolet matkasta:", muoto(skaalaa(0.5, paikka)))
# @loppu perus

# @alku normit
def normi1(v: Vektori) -> float:
    return sum(abs(x) for x in v)


def normi2(v: Vektori) -> float:
    return math.sqrt(sum(x * x for x in v))


def normi_inf(v: Vektori) -> float:
    return max(abs(x) for x in v)


print(f"linnuntie (L2):       {normi2(paikka):.3f} m")
print(f"korttelimatka (L1):   {normi1(paikka):.3f} m")
print(f"suurin poikkeama (L∞): {normi_inf(paikka):.3f} m")
yksikko = skaalaa(1 / normi2(paikka), paikka)
print("yksikkövektori:", muoto(yksikko), f"pituus {normi2(yksikko):.3f}")
# @loppu normit

# @alku numpy
p = np.array(paikka)
print("NumPy:", [f"{np.linalg.norm(p, k):.3f}" for k in (2, 1, np.inf)])
# @loppu numpy
