"""IQ-epatasapaino: peilikuva ja sokea korjaus tilastoista."""

import numpy as np

fs, n = 912e3, 1 << 16
k = np.arange(n)
binni = round(50e3 / fs * n)
w = 2 * np.pi * binni / n


# @alku malli
def epatasapaino(i: np.ndarray, q: np.ndarray, eps: float,
                 phi: float) -> np.ndarray:
    """Q-haaran vahvistus 1 + eps ja vaihevirhe phi radiaaneina."""
    q_vaara = (1 + eps) * (q * np.cos(phi) + i * np.sin(phi))
    tulos: np.ndarray = i + 1j * q_vaara
    return tulos


def peilivaimennus(z: np.ndarray) -> float:
    """Halutun 50 kHz:n ja peilikuvan -50 kHz teho-suhde dB:na."""
    Z = np.fft.fft(z)
    return float(20 * np.log10(abs(Z[binni]) / abs(Z[-binni])))


def teoria(eps: float, phi: float) -> float:
    g = 1 + eps
    return float(10 * np.log10((1 + 2 * g * np.cos(phi) + g * g)
                               / (1 - 2 * g * np.cos(phi) + g * g)))
# @loppu malli


# @alku korjaus
def korjaa(z: np.ndarray) -> np.ndarray:
    """Sokea korjaus: ympyrasymmetrisen signaalin I ja Q ovat yhta
    voimakkaita ja korreloimattomia. Gram-Schmidt: Q:sta poistetaan
    I:n suuntainen osa ja tehot tasataan."""
    i, q = z.real, z.imag
    q = q - np.mean(i * q) / np.mean(i * i) * i
    q *= np.sqrt(np.mean(i * i) / np.mean(q * q))
    tulos: np.ndarray = i + 1j * q
    return tulos
# @loppu korjaus


# @alku ajo
rng = np.random.default_rng(7)
# Mitattava aani ja laajakaistainen "muu liikenne", joka tekee
# signaalista ympyrasymmetrisen, kuten oikeassa kaistassa.
muu = 0.3 * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
ihanne = np.exp(1j * w * k) + muu
print("vahvistusvirhe  vaihevirhe  peilivaimennus  teoria  korjattuna")
for eps, aste in ((0.01, 1.0), (0.05, 3.0), (0.10, 6.0)):
    phi = np.radians(aste)
    z = epatasapaino(ihanne.real, ihanne.imag, eps, phi)
    print(f"{100 * eps:10.0f} %  {aste:6.0f} ast. {peilivaimennus(z):11.1f} "
          f"dB {teoria(eps, phi):6.1f} {peilivaimennus(korjaa(z)):8.0f} dB")
# @loppu ajo
