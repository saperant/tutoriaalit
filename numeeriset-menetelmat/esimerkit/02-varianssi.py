"""Kolme varianssialgoritmia: matemaattisesti samat, numeerisesti eri."""

import statistics

# Mittaukset suuren tasoarvon ympärillä: keskiarvo 1e9, todellinen
# otosvarianssi 30 (tarkka arvo lasketaan murtoluvuilla).
data = [1e9 + d for d in (4.0, 7.0, 13.0, 16.0)]


# @alku yksivaihe
def yksivaihe(x: list[float]) -> float:
    """Oppikirjakaava (summa x^2 - n * keskiarvo^2) / (n - 1)."""
    n = len(x)
    s, s2 = sum(x), sum(v * v for v in x)
    return (s2 - s * s / n) / (n - 1)
# @loppu yksivaihe


# @alku kaksivaihe
def kaksivaihe(x: list[float]) -> float:
    """Ensin keskiarvo, sitten poikkeamien neliöt."""
    ka = sum(x) / len(x)
    return sum((v - ka) ** 2 for v in x) / (len(x) - 1)


def welford(x: list[float]) -> float:
    """Yhden kierroksen päivittyvä algoritmi (Welford 1962)."""
    ka, m2 = 0.0, 0.0
    for k, v in enumerate(x, start=1):
        delta = v - ka
        ka += delta / k
        m2 += delta * (v - ka)
    return m2 / (len(x) - 1)
# @loppu kaksivaihe


# @alku vertailu
tarkka = float(statistics.variance([int(v) for v in data]))
for nimi, f in [("yksivaihe", yksivaihe), ("kaksivaihe", kaksivaihe),
                ("Welford", welford)]:
    print(f"{nimi:10s} {f(data):12.4f}   (tarkka {tarkka:.1f})")
# @loppu vertailu
