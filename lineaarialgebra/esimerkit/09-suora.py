"""Pienimmän neliösumman sovitus: anturin kalibrointi suoralla."""

import numpy as np

# @alku data
# Lämpötila-anturin jännite (V) tunnetuissa lämpötiloissa (°C).
# Mittauksissa on kohinaa, joten suora ei kulje kaikkien pisteiden kautta.
lampo = np.array([0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0])
jannite = np.array([0.502, 0.597, 0.708, 0.795, 0.903, 1.004, 1.091])

# Malli u = a + b·T. Jokainen mittaus on yksi yhtälö, tuntemattomia on
# kaksi: ylimääräytynyt yhtälöryhmä Ax ≈ u.
A = np.column_stack([np.ones_like(lampo), lampo])
# @loppu data

# @alku normaali
# Normaaliyhtälöt A^T A x = A^T u: virhevektori on kohtisuorassa A:n
# sarakeavaruutta vastaan.
x_normaali = np.linalg.solve(A.T @ A, A.T @ jannite)
# @loppu normaali

# @alku qr
# QR: A = QR, jolloin Rx = Q^T u. Ei muodosta A^T A:ta, joten ehtoluku
# ei neliöidy.
Q, R = np.linalg.qr(A)
x_qr = np.linalg.solve(R, Q.T @ jannite)
# @loppu qr

# @alku tulos
a, b = x_qr
print(f"u = {a:.4f} V + {b * 1000:.3f} mV/°C · T")
print("normaaliyhtälöt = QR:", bool(np.allclose(x_normaali, x_qr)))
x_lstsq, *_ = np.linalg.lstsq(A, jannite, rcond=None)
print("np.linalg.lstsq sama:", bool(np.allclose(x_lstsq, x_qr)))
jaannos = jannite - A @ x_qr
print(f"suurin poikkeama: {np.max(np.abs(jaannos)) * 1000:.1f} mV")
print("jäännös kohtisuorassa sarakkeita vastaan:",
      bool(np.allclose(A.T @ jaannos, 0)))
mitattu = 0.850
print(f"jännite {mitattu} V -> {(mitattu - a) / b:.1f} °C")
# @loppu tulos

# @alku projektio
# Projektiomatriisi P = A (A^T A)^-1 A^T vie minkä tahansa
# mittausvektorin lähimpään sarakeavaruuden pisteeseen.
P = A @ np.linalg.solve(A.T @ A, A.T)
print("P u = A x:", bool(np.allclose(P @ jannite, A @ x_qr)))
print("P P = P (projektio kahdesti = kerran):", bool(np.allclose(P @ P, P)))
print("P symmetrinen:", bool(np.allclose(P, P.T)))
# @loppu projektio
