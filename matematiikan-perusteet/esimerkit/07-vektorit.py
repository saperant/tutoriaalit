"""Tason vektorit: pituus, pistetulo, kulma ja projektio."""

import numpy as np
import sympy as sp

# @alku tarkasti
a = sp.Matrix([3, 4])
b = sp.Matrix([4, -2])
print("a + b =", list(a + b), " 2a =", list(2 * a))
print("|a| =", a.norm(), " |b| =", b.norm())
print("a . b =", a.dot(b))
kulma = sp.acos(a.dot(b) / (a.norm() * b.norm()))
print("kulma:", kulma, "=", round(float(sp.deg(kulma)), 2), "astetta")
# @loppu tarkasti

# @alku projektio
projektio = (a.dot(b) / b.dot(b)) * b
kohtisuora = a - projektio
print("a:n projektio b:lle:", list(projektio))
print("kohtisuora osa:", list(kohtisuora),
      " pistetulo b:n kanssa:", kohtisuora.dot(b))
# @loppu projektio

# @alku numpy
an = np.array([3.0, 4.0])
bn = np.array([4.0, -2.0])
cos_kulma = an @ bn / (np.linalg.norm(an) * np.linalg.norm(bn))
print(f"NumPy: |a| = {np.linalg.norm(an):.1f}, "
      f"kulma {np.degrees(np.arccos(cos_kulma)):.2f} astetta")
# Pyöristys voi viedä kosinin yli yhden: arccos antaa silloin NaN.
c = np.array([0.1, 0.7])
cos_c = c @ c / (np.linalg.norm(c) ** 2)
with np.errstate(invalid="ignore"):          # ei varoitusta tulosteeseen
    print("kosini:", repr(float(cos_c)), " arccos:",
          float(np.arccos(cos_c)))
print("rajattuna:", float(np.arccos(np.clip(cos_c, -1.0, 1.0))))
# @loppu numpy
