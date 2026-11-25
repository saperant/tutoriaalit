"""Ylivuotovärähtely: toisen asteen IIR-suodatin ilman syötettä.

Kiertävä tila jää heilumaan täydellä amplitudilla, saturoiva vaimenee.
"""

from collections.abc import Callable

SKAALA = 1 << 15                          # tila on Q1.15
A1 = round(1.1 * (1 << 14))               # kertoimet Q2.14
A2 = round(-0.9 * (1 << 14))              # navat säteellä 0,95: stabiili


# @alku suodatin
def kierra(x: int) -> int:
    return (x + SKAALA) % (2 * SKAALA) - SKAALA


def saturoi(x: int) -> int:
    return max(-SKAALA, min(SKAALA - 1, x))


def vapaa_vaste(kavenna: Callable[[int], int], y1: int, y2: int,
                maara: int) -> list[int]:
    """y[n] = a1 y[n-1] + a2 y[n-2] ilman syötettä; tulo Q3.29 -> Q1.15."""
    tulos = []
    for _ in range(maara):
        kertyma = A1 * y1 + A2 * y2
        y = kavenna((kertyma + (1 << 13)) >> 14)     # puolikas ylöspäin
        tulos.append(y)
        y1, y2 = y, y1
    return tulos
# @loppu suodatin


# @alku koe
alku = round(0.8 * SKAALA)                # tila ennen syötteen loppumista
for nimi, kavenna in (("kierto", kierra), ("saturaatio", saturoi)):
    y = vapaa_vaste(kavenna, alku, -alku, 400)
    alussa = " ".join(f"{v / SKAALA:+.2f}" for v in y[:6])
    huippu = max(abs(v) for v in y[-100:])
    print(f"{nimi:10} {alussa} ... lopussa huippu {huippu} LSB"
          f" ({huippu / SKAALA:.4f})")
# @loppu koe
