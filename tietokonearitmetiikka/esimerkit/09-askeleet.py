"""NumPy-taulukon muoto, askeleet ja näkymät."""

import numpy as np

# @alku askeleet
a = np.arange(12, dtype=np.float64).reshape(3, 4)
print(a.shape, a.strides, a.flags["C_CONTIGUOUS"])
t = a.T                                  # transpoosi: vain askeleet
print(t.shape, t.strides, t.flags["C_CONTIGUOUS"],
      np.shares_memory(a, t))
s = a[:, 1::2]                           # joka toinen sarake
print(s.shape, s.strides, np.shares_memory(a, s))
# @loppu askeleet
# @alku kopio
r = t.reshape(12)                        # ei onnistu askelilla: kopio
print(np.shares_memory(a, r), r[:4])
s[0, 0] = -1.0                           # näkymän kautta muuttuu a
print(a[0])
c = np.ascontiguousarray(t)              # tiivis kopio
print(c.strides)
# @loppu kopio
