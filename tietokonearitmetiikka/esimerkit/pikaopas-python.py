"""Pikaoppaan Python-mallit."""

import math
import struct
from decimal import ROUND_HALF_UP, Decimal

import numpy as np

# @alku python
print(struct.pack("<d", 0.1).hex(), (0.1).hex(), Decimal(0.1))
print(math.isclose(0.1 + 0.2, 0.3), math.fsum([0.1] * 10))
print(-7 // 2, -7 % 2, math.ulp(1.0))
print(Decimal("2.675").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
x = np.array([200, 100], dtype=np.uint8)
print(x + x, (x.astype(np.int32) + x).clip(0, 255).astype(np.uint8))
a = np.arange(6.0).reshape(2, 3)
print(a.strides, a.T.strides, np.shares_memory(a, a.T))
# @loppu python
