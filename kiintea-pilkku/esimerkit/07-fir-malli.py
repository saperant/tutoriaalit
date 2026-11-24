"""Bittitarkka Python-malli samasta Q1.15-FIR-suodattimesta.

Tuloste on bitilleen sama kuin C-toteutuksen (07-fir.c), joten mallia
voi käyttää laitteiston testipenkin referenssinä.
"""

H = [37, -128, -525, -667, 687, 4080, 8012, 9779,
     8012, 4080, 687, -667, -525, -128, 37]
NAYTTEET = 200


# @alku syote
def syote(maara: int) -> list[int]:
    """Sama lineaarinen kongruenssigeneraattori kuin C:ssä."""
    tila, tulos = 12345, []
    for _ in range(maara):
        tila = (tila * 1103515245 + 12345) % (1 << 32)
        tulos.append((tila >> 16) - 32768)
    return tulos
# @loppu syote


# @alku malli
def pyorista_parilliseen(kertyma: int, k: int) -> int:
    """Jako 2^k:lla pyöristäen lähimpään parilliseen.

    Pythonin >> on aina aritmeettinen (lattia), myös negatiivisilla."""
    q, jaannos = kertyma >> k, kertyma & ((1 << k) - 1)
    puolikas = 1 << (k - 1)
    if jaannos > puolikas or (jaannos == puolikas and q & 1):
        q += 1
    return q


def saturoi16(x: int) -> int:
    return max(-32768, min(32767, x))


def suodata(ikkuna: list[int]) -> int:
    kertyma = sum(h * x for h, x in zip(H, ikkuna, strict=True))
    return saturoi16(pyorista_parilliseen(kertyma, 15))
# @loppu malli


# @alku ajo
x = [0] * (len(H) - 1) + syote(NAYTTEET)
tarkiste, suurin_ero = 2166136261, 0.0
for n in range(NAYTTEET):
    ikkuna = [x[n + len(H) - 1 - k] for k in range(len(H))]
    y = suodata(ikkuna)
    viite = sum(h / 32768 * (v / 32768) for h, v in zip(H, ikkuna,
                                                         strict=True))
    suurin_ero = max(suurin_ero, abs(y - viite * 32768))
    tarkiste = ((tarkiste ^ (y & 0xFFFF)) * 16777619) % (1 << 32)
    if n < 6:
        print(f"y[{n}] = {y:6d}")
print(f"tarkiste {tarkiste:08x}")
print(f"suurin ero double-laskentaan {suurin_ero:.3f} LSB")
# @loppu ajo
