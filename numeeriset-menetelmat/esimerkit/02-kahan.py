"""Summauksen virhe: tavallinen, Kahanin ja parittainen summa.

Lasketaan 32-bittisillä liukuluvuilla (float32, noin 7 numeroa), jotta
erot näkyvät jo sadallatuhannella termillä.
"""

import math

import numpy as np

N = 100_000
termit = [np.float32(1.0) / np.float32(k) for k in range(1, N + 1)]
tarkka = math.fsum(float(t) for t in termit)  # termien tarkka summa


# @alku kahan
def kahan(xs: list[np.float32]) -> np.float32:
    """Kompensoitu summa: c kerää jokaisen yhteenlaskun pyöristysvirheen."""
    s, c = np.float32(0.0), np.float32(0.0)
    for x in xs:
        y = x - c
        t = s + y
        c = (t - s) - y      # (t - s) on se osa y:stä, joka meni summaan
        s = t
    return s
# @loppu kahan


# @alku vertailu
tavallinen = np.float32(0.0)
for t in termit:
    tavallinen += t
parittainen = np.sum(np.array(termit, dtype=np.float32))
eps32 = float(np.finfo(np.float32).eps)
for nimi, s in [("tavallinen", tavallinen), ("Kahan", kahan(termit)),
                ("np.sum", parittainen)]:
    virhe = abs(float(s) - tarkka) / tarkka
    print(f"{nimi:10s} suhteellinen virhe {virhe / eps32:5.0f} eps")
print(f"tavallisen summan raja (n-1) eps = {N - 1} eps")
# @loppu vertailu
