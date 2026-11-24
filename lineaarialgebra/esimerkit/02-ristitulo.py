"""Ristitulo: kolmion normaali, pinta-ala ja takapintojen karsinta."""

import math

import numpy as np

Vektori = list[float]


def miinus(a: Vektori, b: Vektori) -> Vektori:
    return [x - y for x, y in zip(a, b, strict=True)]


def piste(a: Vektori, b: Vektori) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))


# @alku risti
def risti(a: Vektori, b: Vektori) -> Vektori:
    """Kolmiulotteisten vektorien ristitulo a × b."""
    return [a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]


def kolmio(p0: Vektori, p1: Vektori, p2: Vektori) -> tuple[Vektori, float]:
    """Kolmion normaali (vastapäivään kiertävistä kärjistä) ja ala."""
    n = risti(miinus(p1, p0), miinus(p2, p0))
    pituus = math.sqrt(piste(n, n))
    return [x / pituus for x in n], pituus / 2


n, ala = kolmio([0.0, 0.0, 0.0], [4.0, 0.0, 0.0], [0.0, 3.0, 0.0])
print(f"normaali {n}, pinta-ala {ala:.1f}")
# @loppu risti

# @alku karsinta
# Kamera katsoo origosta negatiivisen z-akselin suuntaan. Kolmio on
# kameraan päin, jos sen normaali osoittaa kameraa kohti.
kamera = [0.0, 0.0, 0.0]
for nimi, karjet in [("etupinta", [[-1.0, -1.0, -5.0], [1.0, -1.0, -5.0],
                                   [0.0, 1.0, -5.0]]),
                     ("takapinta", [[-1.0, -1.0, -5.0], [0.0, 1.0, -5.0],
                                    [1.0, -1.0, -5.0]])]:
    n, _ = kolmio(*karjet)
    kameraan = miinus(kamera, karjet[0])
    print(f"{nimi}: n·(kamera-p) = {piste(n, kameraan):5.1f} -> "
          f"{'piirretään' if piste(n, kameraan) > 0 else 'karsitaan'}")
# @loppu karsinta

a, b = [1.0, 2.0, 3.0], [4.0, 5.0, 6.0]
print("NumPy sama:", np.allclose(np.cross(a, b), risti(a, b)))
