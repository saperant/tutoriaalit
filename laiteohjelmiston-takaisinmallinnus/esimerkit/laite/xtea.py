"""XTEA-salaus tehtaan työkaluille (vastine laitteen xtea.c:lle)."""

MASKI = 0xFFFFFFFF
DELTA = 0x9E3779B9


def salaa(v0: int, v1: int, avain: tuple[int, int, int, int]
          ) -> tuple[int, int]:
    summa = 0
    for _ in range(32):
        v0 = (v0 + ((((v1 << 4) ^ (v1 >> 5)) + v1)
                    ^ (summa + avain[summa & 3]))) & MASKI
        summa = (summa + DELTA) & MASKI
        v1 = (v1 + ((((v0 << 4) ^ (v0 >> 5)) + v0)
                    ^ (summa + avain[(summa >> 11) & 3]))) & MASKI
    return v0, v1
