"""FM:n kynnysilmio: lahtosignaalin SNR kantoaalto-kohinasuhteen funktiona."""

import numpy as np
from scipy import signal

fs, B, W = 456e3, 200e3, 15e3          # naytetaajuus, kanava, aanikaista
poikkeama, aani = 50e3, 1e3
rng = np.random.default_rng(13)
n = np.arange(round(0.2 * fs))
t = n / fs
z0 = np.exp(1j * poikkeama / aani * np.sin(2 * np.pi * aani * t))
kanava = signal.firwin(129, B / 2, fs=fs)


# @alku mittaa
def lahto_snr(cnr_db: float) -> float:
    """Kohina 200 kHz:n kanavassa, ilmaisu, aanikaista ja SNR."""
    n0 = 10 ** (-cnr_db / 10) / B             # kantoaallon teho 1
    w = np.sqrt(n0 * fs / 2) * (rng.standard_normal(len(n))
                                + 1j * rng.standard_normal(len(n)))
    z = signal.lfilter(kanava, [1.0], z0 + w)
    f = np.angle(z[1:] * np.conj(z[:-1])) * fs / (2 * np.pi)
    F = np.fft.rfft(f[1000:] * np.hanning(len(f) - 1000))
    taajuudet = np.fft.rfftfreq(len(f) - 1000, 1 / fs)
    aanikaista = (taajuudet > 20) & (taajuudet < W)
    oma = np.abs(taajuudet - aani) < 30
    teho = np.abs(F) ** 2
    return float(10 * np.log10(teho[oma].sum()
                               / teho[aanikaista & ~oma].sum()))
# @loppu mittaa


# @alku teoria
# Kynnyksen ylapuolella: SNR = 1,5 (df / W)^2 (B / W) CNR.
vahvistus = 10 * np.log10(1.5 * (poikkeama / W) ** 2 * B / W)
print(f"FM-vahvistus kynnyksen ylapuolella {vahvistus:.1f} dB")
print(" CNR   lahdon SNR   teoria")
for cnr in (2, 4, 6, 8, 10, 12, 15, 20, 25):
    print(f"{cnr:3} dB {lahto_snr(cnr):8.1f} dB {cnr + vahvistus:6.1f} dB")
# @loppu teoria
