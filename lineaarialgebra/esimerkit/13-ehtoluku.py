"""Ehtoluku käytännössä: Hilbertin matriisi vie tarkkuuden."""

import numpy as np

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

# @alku singulaariarvot
# 2-normin ehtoluku on suurimman ja pienimmän singulaariarvon suhde.
i = np.arange(4)
H = 1.0 / (i[:, None] + i[None, :] + 1)
s = np.linalg.svd(H, compute_uv=False)
print("cond(H) = s_max / s_min:",
      bool(np.isclose(np.linalg.cond(H), s[0] / s[-1])))
# @loppu singulaariarvot
