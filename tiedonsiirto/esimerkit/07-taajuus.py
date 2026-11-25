"""Taajuusvirheen avoin estimointi QPSK:sta neljännellä potenssilla."""

import numpy as np

rng = np.random.default_rng(20)

# @alku potenssi
# QPSK-symbolin neljäs potenssi on vakio (-1), joten s^4 e^{i 4 w n}
# on puhdas sini taajuudella 4 w: modulaatio katoaa, taajuus jää.
n = 4_096
b = rng.integers(0, 2, (2, n))
s = ((1 - 2 * b[0]) + 1j * (1 - 2 * b[1])) / np.sqrt(2)
arvot = {complex(round(v.real, 9), round(v.imag, 9)) + 0j for v in s**4}
print(f"QPSK:n neljännet potenssit: {sorted(map(str, arvot))}")


def estimoi(r: np.ndarray) -> float:
    """Taajuus sykleinä symbolia kohti FFT:n huipusta ja interpoloiden."""
    pituus = 8 * len(r)                       # nollilla täyttö tarkentaa
    S = np.abs(np.fft.fft(r**4, pituus))
    huippu = int(np.argmax(S))
    taajuus = np.fft.fftfreq(pituus)[huippu]
    return float(taajuus / 4)
# @loppu potenssi


# @alku koe
print("todellinen   arvio      virhe     (sykliä/symboli)")
N0 = 10 ** (-10 / 10)                         # Es/N0 = 10 dB
for f in (0.0013, -0.02, 0.1, 0.13):
    r = s * np.exp(2j * np.pi * f * np.arange(n) + 0.4j)
    r += np.sqrt(N0 / 2) * (rng.standard_normal(n)
                            + 1j * rng.standard_normal(n))
    arvio = estimoi(r)
    virhe = round(arvio - f, 5) + 0.0
    print(f"{f:+10.4f}  {arvio:+9.5f}  {virhe:+9.5f}")
# @loppu koe
