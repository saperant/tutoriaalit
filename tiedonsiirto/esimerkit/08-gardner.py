"""Symbolitahdistus Gardnerin ajoitusvirheilmaisimella ja interpoloinnilla."""

import numpy as np

rng = np.random.default_rng(14)
hieno, sps, beta = 64, 8, 0.5                 # mallin ja vastaanottimen tahti


def rrc(osuus: int, janne: int = 8) -> np.ndarray:
    t = np.arange(-janne * osuus // 2, janne * osuus // 2 + 1) / osuus
    h = np.empty_like(t)
    for i, ti in enumerate(t):
        if np.isclose(ti, 0.0):
            h[i] = 1 + beta * (4 / np.pi - 1)
        elif np.isclose(abs(ti), 1 / (4 * beta)):
            h[i] = beta / np.sqrt(2) * (
                (1 + 2 / np.pi) * np.sin(np.pi / (4 * beta))
                + (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta)))
        else:
            h[i] = (np.sin(np.pi * ti * (1 - beta))
                    + 4 * beta * ti * np.cos(np.pi * ti * (1 + beta))) / (
                np.pi * ti * (1 - (4 * beta * ti) ** 2))
    tulos: np.ndarray = h / np.sqrt(np.sum(h**2))
    return tulos


# @alku kanava
# "Analoginen" signaali mallinnetaan 64 näytteellä symbolia kohti.
n = 3_000
b = rng.integers(0, 2, (2, n))
symbolit = ((1 - 2 * b[0]) + 1j * (1 - 2 * b[1])) / np.sqrt(2)
nostettu = np.zeros(n * hieno, dtype=complex)
nostettu[::hieno] = symbolit
h = rrc(hieno)
analoginen = np.convolve(np.convolve(nostettu, h), h)   # lähetin + sovitettu
viive = len(h) - 1                            # symbolin 0 huippu
# Vastaanottimen kello: tuntematon vaihe 0.1 T ja 200 ppm:n taajuusvirhe.
vaihe, ppm = 0.1, 200e-6
askel = hieno / sps * (1 + ppm)
paikat = viive - vaihe * hieno + askel * np.arange(int(n * sps * 0.995))
x = (np.interp(paikat, np.arange(len(analoginen)), analoginen.real)
     + 1j * np.interp(paikat, np.arange(len(analoginen)), analoginen.imag))
x += 0.05 * (rng.standard_normal(len(x)) + 1j * rng.standard_normal(len(x)))
# @loppu kanava


# @alku gardner
def lue(t: float) -> complex:
    """Näyte murtoindeksistä: lineaarinen interpolointi (8 näytettä/T)."""
    i = int(t)
    m = t - i
    return complex((1 - m) * x[i] + m * x[i + 1])


def tahdista(Kp: float, Ki: float) -> tuple[np.ndarray, np.ndarray]:
    """Gardner-silmukka. Palauttaa näytteiden paikat ja arvot."""
    t, integraali, edellinen = float(sps), 0.0, 0j
    ajat, naytteet = [], []
    while t + sps + 2 < len(x):
        nykyinen, keski = lue(t), lue(t - sps / 2)
        # Gardner: keskikohdan näyte kertoo, kumpaan suuntaan siirtyä.
        e = float(np.real((nykyinen - edellinen) * np.conj(keski)))
        ajat.append(t)
        naytteet.append(nykyinen)
        integraali += Ki * e
        t += sps - (Kp * e + integraali)      # myöhässä: e > 0
        edellinen = nykyinen
    return np.array(ajat), np.array(naytteet)
# @loppu gardner


# @alku tulos
for nimi, Ki in (("1. aste", 0.0), ("2. aste", 0.001)):
    ajat, y = tahdista(0.1, Ki)
    # Mallista tiedetään symbolin k huipun paikka vastaanottimen näytteinä.
    k = np.rint(ajat * askel / hieno - vaihe).astype(int)
    virhe = (ajat - (k + vaihe) * hieno / askel) / sps      # T:n osina
    loppu = slice(len(y) // 2, None)
    lahella = np.abs(virhe) < 0.05
    lukittu = int(np.argmax(np.convolve(lahella, np.ones(50), "valid") == 50))
    evm = np.sqrt(np.mean(np.abs(y[loppu] - symbolit[k[loppu]]) ** 2))
    print(f"{nimi}: lukittui {lukittu} symbolissa, virhe lopussa"
          f" {np.mean(virhe[loppu]):+.3f} +- {np.std(virhe[loppu]):.3f} T,"
          f" EVM {100 * evm:.1f} %")
# Ilman tahdistusta: joka 8. näyte. Kello liukuu 200 ppm eli 0.0002 T
# symbolia kohti, joten näytteiden paikka symbolissa muuttuu.
kiintea = np.arange(sps, len(x) - 1, sps)
kk = np.rint(kiintea * askel / hieno - vaihe).astype(int)
for alku in (0, 1_000, 2_000):
    osa = slice(alku, alku + 500)
    e = np.sqrt(np.mean(np.abs(x[kiintea[osa]] - symbolit[kk[osa]]) ** 2))
    print(f"ilman tahdistusta, symbolit {alku:4d}-{alku + 500:4d}:"
          f" EVM {100 * e:5.1f} %")
# @loppu tulos
