"""Polynomisovitus: ylisovitus ja normaaliyhtälöiden ehtoluku."""

import numpy as np

rng = np.random.default_rng(2026)
x = np.linspace(0.0, 1.0, 12)
y = np.sin(2 * np.pi * x) + rng.normal(0.0, 0.1, x.size)
testi_x = np.linspace(0.02, 0.98, 50)
testi_y = np.sin(2 * np.pi * testi_x)

# @alku asteet
for aste in (1, 3, 5, 11):
    V = np.vander(x, aste + 1, increasing=True)     # sarakkeet 1, x, x²…
    kertoimet, *_ = np.linalg.lstsq(V, y, rcond=None)
    sovitus = np.vander(testi_x, aste + 1, increasing=True) @ kertoimet
    opetus = np.sqrt(np.mean((V @ kertoimet - y) ** 2))
    testi = np.sqrt(np.mean((sovitus - testi_y) ** 2))
    print(f"aste {aste:>2}: virhe opetusdatassa {opetus:5.3f}, "
          f"uusissa pisteissä {'yli 1' if testi > 1 else f'{testi:5.3f}'}")
# @loppu asteet

# @alku ehtoluku
for aste in (3, 7):
    V = np.vander(x, aste + 1, increasing=True)
    kv, kn = np.linalg.cond(V), np.linalg.cond(V.T @ V)
    print(f"aste {aste}: cond(V) ~1e{np.log10(kv):.0f}, "
          f"cond(V^T V) ~1e{np.log10(kn):.0f}")
# @loppu ehtoluku
