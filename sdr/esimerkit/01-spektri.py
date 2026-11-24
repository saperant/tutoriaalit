"""Ensimmainen katsaus kaistaan: tehospektri ja signaalien haku."""

import numpy as np
from scipy import signal

# @alku tallenne
fs, keskitaajuus = 912e3, 98.0e6      # RTL-SDR viritetty 98,0 MHz:iin
rng = np.random.default_rng(1)
n = np.arange(round(0.05 * fs))       # 50 ms
t = n / fs


def fm_asema(f0: float, teho_db: float) -> np.ndarray:
    """FM-asema, jonka ohjelmana on 15 kHz:iin rajattu kohina."""
    sos = signal.butter(6, 15e3, fs=fs, output="sos")
    ohjelma = signal.sosfilt(sos, rng.standard_normal(len(n)))
    ohjelma /= 3 * np.std(ohjelma)              # huiput noin +-1
    vaihe = 2 * np.pi * 75e3 * np.cumsum(ohjelma) / fs
    a = 10 ** (teho_db / 20)
    tulos: np.ndarray = a * np.exp(1j * (2 * np.pi * f0 * t + vaihe))
    return tulos


x = (fm_asema(200e3, 0.0) + fm_asema(-250e3, -20.0)
     + 0.003 * np.exp(2j * np.pi * -60e3 * t))       # kapea kantoaalto
x += 0.01 * (rng.standard_normal(len(n)) + 1j * rng.standard_normal(len(n)))
# @loppu tallenne

# @alku spektri
f, psd = signal.welch(x, fs, nperseg=4096, return_onesided=False,
                      scaling="density")
f, psd = np.fft.fftshift(f), np.fft.fftshift(psd)
db = 10 * np.log10(psd)
lattia = np.median(db)                # kohinalattia: puolet kaistasta tyhja
print(f"kohinalattia {lattia:.0f} dB/Hz, resoluutio {fs / 4096:.0f} Hz")
for alku in range(0, len(f), 256):    # 16 kaistaa a 57 kHz
    osa = db[alku:alku + 256]
    yli = max(0.0, float(osa.max() - lattia))
    print(f"{(keskitaajuus + f[alku]) / 1e6:7.3f} MHz "
          f"{'#' * round(yli / 2):<26} {yli:4.0f} dB")
# @loppu spektri

# @alku haku
# Kynnys 10 dB lattian ylapuolella; alle 10 kHz:n aukot yhdistetaan.
kaistat: list[list[int]] = []
for i in np.flatnonzero(db > lattia + 10):
    if kaistat and i - kaistat[-1][1] <= 10e3 / (fs / 4096):
        kaistat[-1][1] = int(i)
    else:
        kaistat.append([int(i), int(i)])
for a, b in kaistat:
    paino = psd[a:b + 1]
    keski = float(np.sum(f[a:b + 1] * paino) / paino.sum())
    teho = 10 * np.log10(paino.sum() * fs / 4096)
    print(f"signaali {(keskitaajuus + keski) / 1e6:8.3f} MHz, "
          f"leveys {(f[b] - f[a]) / 1e3:4.0f} kHz, teho {teho:4.0f} dB")
# @loppu haku
