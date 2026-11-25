"""Älä laske käänteismatriisia, kun tarvitset ratkaisun."""

import numpy as np

# @alku vertailu
rng = np.random.default_rng(1)
n = 200
# Huonokuntoinen matriisi: singulaariarvot 1 … 1e-10.
U, _ = np.linalg.qr(rng.normal(size=(n, n)))
V, _ = np.linalg.qr(rng.normal(size=(n, n)))
A = U @ np.diag(np.logspace(0, -10, n)) @ V.T
x_tarkka = rng.normal(size=n)
b = A @ x_tarkka

x_solve = np.linalg.solve(A, b)          # LU + kaksi kolmioratkaisua
x_inv = np.linalg.inv(A) @ b             # käänteismatriisi + kertolasku
for nimi, x in [("solve", x_solve), ("inv @ b", x_inv)]:
    jaannos = np.linalg.norm(A @ x - b) / np.linalg.norm(b)
    print(f"{nimi:<8} suhteellinen jäännös "
          f"{'alle 1e-12' if jaannos < 1e-12 else 'yli 1e-12'}")
# @loppu vertailu
