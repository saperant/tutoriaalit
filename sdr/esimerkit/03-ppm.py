"""Kiteen taajuusvirhe (ppm): mittaus tunnetusta kantoaallosta."""

import numpy as np

fs, n = 912e3, 1 << 18
k = np.arange(n)
rng = np.random.default_rng(10)


# @alku arvio
def taajuus(z: np.ndarray) -> float:
    """Huipun taajuus: FFT nelinkertaisella nollatayttolla ja paraabeli-
    sovitus kolmeen binniin (tarkkuus murto-osa binnista)."""
    m = 4 * len(z)
    S = np.abs(np.fft.fft(z * np.hanning(len(z)), m))
    i = int(np.argmax(S))
    a, b, c = np.log(S[i - 1]), np.log(S[i]), np.log(S[(i + 1) % m])
    siirto = 0.5 * (a - c) / (a - 2 * b + c)
    f = (i + siirto) * fs / m
    return float(f - fs if f > fs / 2 else f)
# @loppu arvio


# @alku mittaus
# Viritys 100,000 MHz:iin; tiedetaan, etta 100,100 MHz:ssa on kantoaalto.
# Halpa kide on 28,8 MHz * (1 + 37 ppm): kaikki taajuudet siirtyvat.
virhe_ppm = 37.0
viritys, kanto = 100.000e6, 100.100e6
nakyva = (kanto - viritys * (1 + virhe_ppm * 1e-6)) / (1 + virhe_ppm * 1e-6)
z = np.exp(2j * np.pi * nakyva * k / fs)
z += 0.3 * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
mitattu = taajuus(z)
print(f"kantoaalto nakyy {mitattu / 1e3:.3f} kHz:ssa (odotus 100 kHz)")
# @loppu mittaus

# @alku korjaus
# Kiteen virhe skaalaa seka virityksen etta naytetaajuuden. Viritys-
# taajuuden siirto f0 * ppm on valtaosa; arvio ensimmaisessa kertaluvussa:
arvio_ppm = (100e3 - mitattu) / kanto * 1e6
print(f"arvioitu kidevirhe {arvio_ppm:.1f} ppm (todellinen {virhe_ppm})")
for f0 in (433.92e6, 868.3e6, 1090e6):
    print(f"{f0 / 1e6:8.2f} MHz:lla siirto olisi "
          f"{f0 * arvio_ppm * 1e-6 / 1e3:4.1f} kHz")
# @loppu korjaus
