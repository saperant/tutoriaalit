"""Pienimmän neliösumman sovitus: normaaliyhtälöt vs. QR-hajotelma."""

import numpy as np

EPS = float(np.finfo(float).eps)

# @alku data
# Asteen 10 polynomi, jonka kertoimet ovat ykkösiä, 50 pisteessä
# välillä [0, 1]. Data on tarkka, joten oikea ratkaisu tunnetaan.
x = np.linspace(0.0, 1.0, 50)
A = np.vander(x, 11, increasing=True)     # sarakkeet 1, x, ..., x^10
oikea = np.ones(11)
y = A @ oikea
kappa = float(np.linalg.cond(A))
print(f"cond(A) = {kappa:.0e}, cond(A^T A) = "
      f"{float(np.linalg.cond(A.T @ A)):.0e}")
# @loppu data

# @alku ratkaisut
normaali = np.linalg.solve(A.T @ A, A.T @ y)   # ehtoluku neliöityy
Q, R = np.linalg.qr(A)                         # A = QR, Q ortogonaalinen
qr = np.linalg.solve(R, Q.T @ y)               # R x = Q^T y
lstsq = np.linalg.lstsq(A, y, rcond=None)[0]   # LAPACK, SVD-pohjainen
# @loppu ratkaisut

# @alku rajat
for nimi, c, raja in [("normaaliyht.", normaali, kappa**2 * EPS),
                      ("QR", qr, kappa * EPS),
                      ("lstsq", lstsq, kappa * EPS)]:
    virhe = float(np.max(np.abs(c - oikea)))
    print(f"{nimi:12s} virhe < 1e-6: {'kyllä' if virhe < 1e-6 else 'ei':5s}"
          f" virhe <= 10 x raja: {'kyllä' if virhe <= 10 * raja else 'ei'}")
print(f"raja QR:lle cond(A) eps = {kappa * EPS:.0e}, "
      f"normaaliyhtälöille cond(A)^2 eps = {kappa**2 * EPS:.0e}")
# @loppu rajat
