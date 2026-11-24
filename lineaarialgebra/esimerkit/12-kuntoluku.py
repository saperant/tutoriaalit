"""Kuntoluku: kuinka paljon syötteen pieni virhe voi kasvaa ratkaisussa."""

import numpy as np

# @alku herkkyys
# Kaksi lähes yhdensuuntaista suoraa: leikkauspiste liikkuu paljon,
# kun toista suoraa siirretään hiukan.
A = np.array([[1.0, 1.0], [1.0, 1.0001]])
b = np.array([2.0, 2.0001])
x = np.linalg.solve(A, b)
x_hairio = np.linalg.solve(A, b + np.array([0.0, 0.0001]))
print("ratkaisu:         ", (np.round(x, 4) + 0.0).tolist())
print("b muuttui 0,0001: ", (np.round(x_hairio, 4) + 0.0).tolist())
print(f"kuntoluku ~{np.linalg.cond(A):.0f}")
# @loppu herkkyys

# @alku hilbert
# Hilbertin matriisi H[i][j] = 1/(i+j+1) on tunnetusti huonokuntoinen.
# Ratkaistaan Hx = b, kun tarkka ratkaisu on ykkösvektori.
print(" n  cond(H)   oikeita desimaaleja (noin)")
for n in (4, 8, 10):
    i = np.arange(n)
    H = 1.0 / (i[:, None] + i[None, :] + 1)
    x_tarkka = np.ones(n)
    x = np.linalg.solve(H, H @ x_tarkka)
    virhe = np.max(np.abs(x - x_tarkka))
    desimaaleja = "yli 10" if virhe < 1e-10 else "alle 6" if virhe > 1e-6 \
        else "6–10"
    print(f"{n:>2}  1e{np.log10(np.linalg.cond(H)):4.1f}   {desimaaleja}")
# @loppu hilbert
