"""Tarkistaa, että mallin kokonaislukukertoimet ovat suunnittelun
kvantisoitu tulos, ja tulostaa FIR-kertoimet kolmessa muodossa.

Käyttö: python3 analyysit/suunnittelu.py
"""

from __future__ import annotations

import sys

from scipy import signal

from malli import kertoimet as k
from malli.kiintea import kvantisoi


def main() -> int:
    virheita = 0

    # @alku fir
    h = signal.firwin(8, 0.5)
    q = [kvantisoi(float(v), k.KERROIN_MURTO, k.KERROIN_BITIT) for v in h]
    print("FIR, signal.firwin(8, 0.5), Q1.15:")
    print(" k  liukuluku   koodi  heksana")
    for i, (v, c) in enumerate(zip(h, q, strict=True)):
        print(f"{i:2}  {v:+.6f}  {c:6}  {c & 0xFFFF:04x}")
    print(
        f"summa {sum(q)} = {sum(q) / (1 << k.KERROIN_MURTO):.4f}, "
        f"itseisarvojen summa {sum(abs(c) for c in q)}"
    )
    # @loppu fir
    virheita += q != k.FIR

    p = signal.firwin(16, 0.25)
    qp = [kvantisoi(float(v), k.KERROIN_MURTO, k.KERROIN_BITIT) for v in p]
    virheita += qp != k.POLYFAASI

    # @alku sos
    sos = signal.butter(4, 0.1, output="sos")
    for i, (_, _, _, _, a1, a2) in enumerate(sos):
        # Vahvistus jaetaan niin, että lohkon DC-vahvistus on 1:
        # H(1) = (b0 + b1 + b2) / (1 + a1 + a2) ja b = g [1, 2, 1].
        g = (1 + a1 + a2) / 4
        lohko = tuple(
            kvantisoi(float(v), k.IIR_MURTO, 16)
            for v in (g, 2 * g, g, a1, a2)
        )
        dc = sum(lohko[:3]) / (sum(lohko[3:]) + (1 << k.IIR_MURTO))
        print(f"SOS-lohko {i}: {lohko}, DC-vahvistus {dc:.4f}")
        virheita += lohko != k.SOS[i]
    # @loppu sos

    if virheita:
        print("VIRHE: kertoimet poikkeavat malli/kertoimet.py:n luvuista")
        return 1
    print("OK: malli/kertoimet.py vastaa suunnittelua")
    return 0


if __name__ == "__main__":
    sys.exit(main())
