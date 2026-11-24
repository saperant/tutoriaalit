"""Siirtofunktio, navat ja nollat sekä askelvaste."""

import numpy as np
import sympy as sp
from scipy import signal

s = sp.symbols("s")
t = sp.symbols("t", positive=True)

# @alku siirto
# Sarja-RLC, lähtönä kondensaattorin jännite: L C u'' + R C u' + u = U.
# Nollilla alkuehdoilla H(s) = U_C(s)/U(s) = 1 / (L C s^2 + R C s + 1).
L_, R_, C_ = sp.Rational(1, 100), 20, sp.Rational(1, 1_000_000)
H = 1 / (L_ * C_ * s**2 + R_ * C_ * s + 1)
print("H(s) =", sp.simplify(H))
navat = sp.solve(sp.denom(sp.together(H)), s)
for p in sorted(navat, key=lambda z: float(sp.im(z))):
    print(f"napa: {float(sp.re(p)):.1f} {float(sp.im(p)):+.1f}j")
# @loppu siirto

# @alku askel
# Askelvaste: tulona yksikköaskel 1/s. Lopullinen arvo s H(s)/s, s -> 0.
askel = sp.inverse_laplace_transform(sp.apart(H / s, s, full=False), s, t)
print("loppuarvo:", sp.limit(s * H / s, s, 0))
# Alivaimennetun vasteen huippu on puolen värähdysjakson kohdalla:
# t_p = pi / w_d, missä w_d on navan imaginaariosa.
wd = max(float(sp.im(p)) for p in navat)
tp = sp.pi / wd
print(
    f"huippu {float(askel.subs(t, tp)):.4f} "
    f"hetkellä {float(tp) * 1000:.4f} ms"
)
# @loppu askel

# @alku scipy
# Sama numeerisesti: kertoimet korkeimmasta potenssista alkaen.
jarjestelma = signal.lti([1.0], [float(L_ * C_), float(R_ * C_), 1.0])
aika = np.linspace(0, 3e-3, 3001)
_, vaste = signal.step(jarjestelma, T=aika)
i = int(np.argmax(vaste))
print(f"scipy: huippu {vaste[i]:.4f} hetkellä {aika[i] * 1000:.4f} ms")
zeta = float(R_ / 2 * sp.sqrt(C_ / L_))
teoria = np.exp(-zeta * np.pi / np.sqrt(1 - zeta**2))
print(f"zeta = {zeta:.3f}, ylitys kaavasta {teoria * 100:.2f} %")
# @loppu scipy
