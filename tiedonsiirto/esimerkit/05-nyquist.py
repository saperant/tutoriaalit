"""Nyquistin ehto: mitkä pulssit ovat symbolien hetkillä nollia?"""

import numpy as np
import numpy.typing as npt

Reaali = npt.NDArray[np.float64]
sps, janne = 16, 16                           # näytettä/symboli, pituus T:inä
t = np.arange(-janne * sps // 2, janne * sps // 2 + 1) / sps   # aika T:inä


# @alku pulssit
def korotettu_kosini(beta: float) -> Reaali:
    """RC-pulssi p(t) = sinc(t) cos(pi beta t) / (1 - (2 beta t)^2)."""
    nimittaja = 1 - (2 * beta * t) ** 2
    raja = np.isclose(nimittaja, 0.0)
    p = np.sinc(t) * np.cos(np.pi * beta * t) / np.where(raja, 1.0, nimittaja)
    tulos: Reaali = np.where(raja, np.pi / 4 * np.sinc(1 / (2 * beta)), p)
    return tulos


def juuri(beta: float) -> Reaali:
    """RRC: pulssi, jonka itsensä kanssa konvoloituna saadaan RC."""
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
    tulos: Reaali = h / np.sqrt(np.sum(h**2))
    return tulos
# @loppu pulssit


# @alku isi
def isi(p: Reaali) -> float:
    """Pahin ISI: muiden symbolien näytteiden itseisarvojen summa / huippu."""
    huippu = int(np.argmax(np.abs(p)))
    naytteet = p[huippu % sps::sps]
    return float((np.sum(np.abs(naytteet)) - abs(p[huippu])) / abs(p[huippu]))


rrc = juuri(0.35)
print(f"sinc (beta = 0)       ISI {isi(np.sinc(t)):.4f}")
print(f"RC, beta = 0.35       ISI {isi(korotettu_kosini(0.35)):.4f}")
print(f"RRC yksin             ISI {isi(rrc):.4f}")
print(f"RRC * RRC (sovitettu) ISI {isi(np.convolve(rrc, rrc)):.4f}")
# @loppu isi

# @alku kaista
print("beta   99 %:n kaista   (1 + beta) / 2T")
for beta in (0.0, 0.25, 0.5, 1.0):
    p = korotettu_kosini(beta) if beta > 0 else np.sinc(t)
    P = np.abs(np.fft.fft(p, 1 << 16)) ** 2
    f = np.abs(np.fft.fftfreq(len(P))) * sps  # taajuus symbolinopeuden 1/T
    jarjestys = np.argsort(f)
    kertyma = np.cumsum(P[jarjestys]) / P.sum()
    B99 = f[jarjestys][np.searchsorted(kertyma, 0.99)]
    print(f"{beta:4.2f}   {B99:9.3f} / T   {(1 + beta) / 2:9.3f} / T")
# @loppu kaista
