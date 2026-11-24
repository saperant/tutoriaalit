"""Liukulukujen erot: summausjarjestys, ULP ja toleranssit."""

import numpy as np

# @alku jarjestys
rng = np.random.default_rng(7)
x = rng.standard_normal(10_000)
h = rng.standard_normal(10_000)
eteen = 0.0
for xi, hi in zip(x, h, strict=True):       # kuten yksinkertainen C-silmukka
    eteen += xi * hi
taakse = 0.0
for xi, hi in zip(x[::-1], h[::-1], strict=True):
    taakse += xi * hi
pistetulo = float(np.dot(x, h))             # BLAS: lohkot ja SIMD
suht = abs(eteen - taakse) / abs(eteen)
print(f"eteen vs. taakse: suhteellinen ero {suht:.0e}")
# BLAS-kirjaston tulos riippuu prosessorista, joten se tarkistetaan
# toleranssilla eika tulosteta sellaisenaan.
print("np.dot samaa luokkaa:", abs(eteen - pistetulo) / abs(eteen) < 1e-12)
# @loppu jarjestys

# @alku ulp
print(f"ULP luvussa 1.0   {np.spacing(1.0):.3e}")
print(f"ULP luvussa 1000  {np.spacing(1000.0):.3e}")
print(f"float32:n ULP 1.0 {np.spacing(np.float32(1.0)):.3e}")
# @loppu ulp

# @alku raja
# Pistetulon virheen ylaraja: n * eps * sum |x_i h_i|.
eps = float(np.finfo(np.float64).eps)
raja = x.size * eps * float(np.sum(np.abs(x * h)))
print(f"ylaraja {raja:.1e}, todellinen ero {abs(eteen - taakse):.0e}")
print("pelkka rtol nollan kohdalla:",
      bool(np.isclose(1e-17, 0.0, rtol=1e-9, atol=0.0)))
print("atol signaalin tasoon:",
      bool(np.isclose(1e-17, 0.0, rtol=1e-9, atol=1e-12)))
# @loppu raja
