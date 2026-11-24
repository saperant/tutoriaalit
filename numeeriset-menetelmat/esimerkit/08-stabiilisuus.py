"""Stabiilisuus: eksplisiittinen ja implisiittinen Euler jäykällä
yhtälöllä y' = lambda (y - cos t) - sin t, tarkka ratkaisu y = cos t."""

import math

LAMBDA = -1000.0


def f(t: float, y: float) -> float:
    return LAMBDA * (y - math.cos(t)) - math.sin(t)


# @alku eulerit
def eksplisiittinen(h: float, n: int) -> tuple[float, float]:
    """n askelta pituudeltaan h; palauttaa (t, y)."""
    y, t = 1.0, 0.0
    for _ in range(n):
        y, t = y + h * f(t, y), t + h
    return t, y


def implisiittinen(h: float, n: int) -> tuple[float, float]:
    """y_(k+1) = y_k + h f(t_(k+1), y_(k+1)). Yhtälö on lineaarinen y:n
    suhteen, joten se ratkeaa suljetusti; yleensä tarvitaan Newton."""
    y, t = 1.0, 0.0
    for _ in range(n):
        t += h
        y = (y + h * (-LAMBDA * math.cos(t) - math.sin(t))) / (1 - h * LAMBDA)
    return t, y
# @loppu eulerit


# @alku vertailu
print(f"stabiilisuusraja eksplisiittiselle: h < 2/|lambda| = "
      f"{2 / abs(LAMBDA):.4f}")
for h in (0.001, 0.0019, 0.0021, 0.0025, 0.01, 0.1):
    n = round(1.0 / h)                   # integroidaan noin hetkeen t = 1
    t, ye = eksplisiittinen(h, n)
    _, yi = implisiittinen(h, n)
    e, i = abs(ye - math.cos(t)), abs(yi - math.cos(t))
    print(f"h = {h:6.4f}: eksplisiittinen virhe {e:8.1e}, "
          f"implisiittinen {i:.1e}")
# @loppu vertailu
