"""Herkkyys ja ehtoluku: kuinka paljon pieni virhe syötteessä voi
kasvaa ratkaisussa."""

import numpy as np

# @alku herkkyys
# Kaksi suoraparia. Oikeaa puolta b häiritään samalla pienellä määrällä,
# ja katsotaan, paljonko leikkauspiste x siirtyy.
hairio = np.array([0.0, 0.0002])
parit = {
    "kohtisuorat": (np.array([[1.0, 1.0], [1.0, -1.0]]),
                    np.array([2.0, 0.0])),
    "lähes yhdensuuntaiset": (np.array([[1.0, 1.0], [1.0, 1.0001]]),
                              np.array([2.0, 2.0001])),
}
for nimi, (A, b) in parit.items():
    x = np.linalg.solve(A, b)
    x_hairio = np.linalg.solve(A, b + hairio)
    syote = np.linalg.norm(hairio) / np.linalg.norm(b)
    tulos = np.linalg.norm(x_hairio - x) / np.linalg.norm(x)
    print(f"{nimi}:")
    print("  ratkaisu", (np.round(x, 4) + 0.0).tolist(), "-> häirittynä",
          (np.round(x_hairio, 4) + 0.0).tolist())
    print(f"  virhe kasvoi {tulos / syote:.0f}-kertaiseksi,",
          f"ehtoluku {np.linalg.cond(A):.0f}")
# @loppu herkkyys
