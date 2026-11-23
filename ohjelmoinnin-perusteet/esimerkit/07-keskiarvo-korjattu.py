"""Keskiarvo, joka ohittaa virheelliset rivit ja kertoo niistä."""

import sys


def jasenna_luku(teksti: str) -> float:
    """Muuntaa tekstin luvuksi. Hyväksyy desimaalipilkun."""
    return float(teksti.strip().replace(",", "."))


luvut = []
virheelliset = []
for numero, rivi in enumerate(sys.stdin, start=1):
    if not rivi.strip():
        continue                     # tyhjät rivit ohitetaan
    try:
        luvut.append(jasenna_luku(rivi))
    except ValueError:
        virheelliset.append(numero)

if virheelliset:
    print(f"Ohitettiin virheelliset rivit: {virheelliset}")
if not luvut:
    print("Ei yhtään lukua, keskiarvoa ei voi laskea.")
    sys.exit(1)
print(f"Lukuja {len(luvut)}, keskiarvo {sum(luvut) / len(luvut):.2f}")
