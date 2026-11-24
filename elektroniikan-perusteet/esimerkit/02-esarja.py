"""E-sarjat: lähin standardiarvo ja toleranssin vaikutus jakajaan."""

import math
from itertools import product

from spice import muotoile

# @alku sarjat
# E12- ja E24-sarjojen arvot yhden dekadin sisällä (IEC 60063).
E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
E24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
       3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]


def lahin(arvo: float, sarja: list[float]) -> float:
    """Lähin sarjan arvo logaritmisella asteikolla."""
    dekadi = 10.0 ** math.floor(math.log10(arvo))
    ehdokkaat = [s * dekadi for s in sarja] + [10 * dekadi]
    return min(ehdokkaat, key=lambda e: abs(math.log(e / arvo)))
# @loppu sarjat


for tavoite in (3300.0, 5000.0, 7000.0):
    print(f"{muotoile(tavoite, 'ohm'):>10}: E12 "
          f"{muotoile(lahin(tavoite, E12), 'ohm'):>10}, E24 "
          f"{muotoile(lahin(tavoite, E24), 'ohm'):>10}")

# @alku huonoin
# Jakaja 10 kohm / 4,7 kohm, 5 %:n vastukset: huonoin tapaus saadaan,
# kun kumpikin vastus on toleranssinsa ääripäässä.
U, R1, R2, tol = 12.0, 10e3, 4.7e3, 0.05
nimellinen = U * R2 / (R1 + R2)
arvot = [U * r2 / (r1 + r2)
         for r1, r2 in product((R1 * (1 - tol), R1 * (1 + tol)),
                               (R2 * (1 - tol), R2 * (1 + tol)))]
print(f"nimellinen {nimellinen:.3f} V, vaihteluväli "
      f"{min(arvot):.3f}...{max(arvot):.3f} V")
# @loppu huonoin
