"""Solukko: taajuuksien uudelleenkäyttö ja häiriö solun reunalla."""

import math

import numpy as np

VAIMENNUSEKSPONENTTI = 3.5      # kaupunkiympäristö


# @alku kuusikulmio
def tukiasemat(kehia: int, etaisyys: float) -> list[tuple[float, float]]:
    """Kuusikulmaisen solukon tukiasemat (aksiaaliset koordinaatit)."""
    pisteet = []
    for q in range(-kehia, kehia + 1):
        for r in range(max(-kehia, -q - kehia), min(kehia, -q + kehia) + 1):
            x = etaisyys * (q + r / 2)
            y = etaisyys * r * math.sqrt(3) / 2
            pisteet.append((x, y))
    return pisteet


def sinr_db(kayttaja: tuple[float, float], uudelleenkaytto: int) -> float:
    """Oma asema on origossa. Häiritsijät ovat niitä samaa taajuutta
    käyttäviä asemia, joiden etäisyys on uudelleenkäyttöetäisyys."""
    etaisyys = math.sqrt(3) * math.sqrt(uudelleenkaytto)   # solusäde 1
    asemat = np.array(tukiasemat(3, etaisyys))
    d = np.hypot(asemat[:, 0] - kayttaja[0], asemat[:, 1] - kayttaja[1])
    teho = d ** -VAIMENNUSEKSPONENTTI
    oma = np.argmin(np.hypot(asemat[:, 0], asemat[:, 1]))
    hairio = float(teho.sum() - teho[oma])
    return 10 * math.log10(float(teho[oma]) / hairio)
# @loppu kuusikulmio


# @alku vertailu
KAISTA = 20e6
for uudelleenkaytto in (1, 3, 7):
    # Solun kulma (etäisyys 1) on yhtä kaukana kolmesta asemasta.
    for nimi, paikka in (("keskellä", (0.3, 0.0)),
                         ("kulmassa", (math.sqrt(3) / 2, 0.5))):
        s = sinr_db(paikka, uudelleenkaytto)
        c = KAISTA / uudelleenkaytto * math.log2(1 + 10 ** (s / 10))
        print(f"uudelleenkäyttö {uudelleenkaytto}, {nimi}: SINR"
              f" {s:5.1f} dB, Shannon {c / 1e6:5.1f} Mbit/s")
# @loppu vertailu
