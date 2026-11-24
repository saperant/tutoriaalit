"""Pienet liukulukumuodot purettuina: binary16, bfloat16 ja FP8."""

import math
from dataclasses import dataclass

import numpy as np


# @alku muoto
@dataclass(frozen=True)
class Muoto:
    nimi: str
    e_bitit: int
    m_bitit: int
    ieee: bool = True      # E4M3: ei ääretöntä, NaN vain S.1111.111

    @property
    def bias(self) -> int:
        return (1 << (self.e_bitit - 1)) - 1

    def arvo(self, koodi: int) -> float:
        """Purkaa bittikuvion liukuluvuksi."""
        m = koodi & ((1 << self.m_bitit) - 1)
        e = (koodi >> self.m_bitit) & ((1 << self.e_bitit) - 1)
        s = -1.0 if koodi >> (self.e_bitit + self.m_bitit) else 1.0
        e_max = (1 << self.e_bitit) - 1
        if self.ieee and e == e_max:
            return s * float("inf") if m == 0 else float("nan")
        if not self.ieee and e == e_max and m == (1 << self.m_bitit) - 1:
            return float("nan")
        if e == 0:                               # subnormaali
            return s * math.ldexp(m, 1 - self.bias - self.m_bitit)
        piilo = m | (1 << self.m_bitit)          # piilobitti näkyviin
        return s * math.ldexp(piilo, e - self.bias - self.m_bitit)
# @loppu muoto


MUODOT = [Muoto("binary16", 5, 10), Muoto("bfloat16", 8, 7),
          Muoto("FP8 E5M2", 5, 2), Muoto("FP8 E4M3", 4, 3, ieee=False)]

# @alku taulukko
print(f"{'muoto':9} {'suurin':>10} {'pienin norm.':>12} {'epsilon':>9}")
for f in MUODOT:
    bitit = 1 + f.e_bitit + f.m_bitit
    arvot = [f.arvo(k) for k in range(2 ** (bitit - 1))]   # positiiviset
    aareliset = [a for a in arvot if np.isfinite(a)]
    normaali = f.arvo(1 << f.m_bitit)
    print(f"{f.nimi:9} {max(aareliset):10.6g} {normaali:12.6g} "
          f"{2.0 ** -f.m_bitit:9.4g}")
# @loppu taulukko

# @alku tarkistus
# Oma purku vastaa NumPyn binary16-tulkintaa kaikilla 65536 koodilla,
# ja bfloat16 on float32:n ylin puolisko.
koodit = np.arange(2**16, dtype=np.uint16)
numpy16 = koodit.view(np.float16).astype(np.float64)
oma16 = np.array([MUODOT[0].arvo(int(k)) for k in koodit])
print("binary16 sama:", np.array_equal(numpy16, oma16, equal_nan=True))
with np.errstate(invalid="ignore"):     # NaN-koodien muunnos
    bf = (koodit.astype(np.uint32) << 16).view(np.float32)
    bf64 = bf.astype(np.float64)
oma_bf = np.array([MUODOT[1].arvo(int(k)) for k in koodit])
print("bfloat16 sama:", np.array_equal(bf64, oma_bf, equal_nan=True))
# @loppu tarkistus
