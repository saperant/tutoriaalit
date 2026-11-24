"""Tasakomponentti (DC-piikki) ja sen poisto."""

import numpy as np
from scipy import signal

fs, n = 912e3, 1 << 17
k = np.arange(n)
rng = np.random.default_rng(6)
# @alku piikki
# Suoramuunnosvastaanottimen paikallisoskillaattori vuotaa ja nakyy
# tasajannitteena: spektrissa piikki tasan keskitaajuudella.
hyotysignaali = 0.1 * np.exp(2j * np.pi * 30e3 * k / fs)
kohina = 1e-3 * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
x = hyotysignaali + kohina + (0.02 - 0.012j)


def tasot(z: np.ndarray) -> tuple[float, float]:
    """Tasakomponentin ja 30 kHz:n signaalin taso dB:na."""
    w = signal.windows.flattop(len(z))       # tarkka amplitudi
    Z = np.fft.fft(z * w) / w.sum()
    return (float(20 * np.log10(abs(Z[0]))),
            float(20 * np.log10(abs(Z[round(30e3 / fs * len(z))]))))


dc, s = tasot(x)
print(f"ennen: tasakomponentti {dc:4.0f} dB, signaali {s:4.0f} dB")
# @loppu piikki

# @alku esto
# DC-esto: derivaattori ja napa lahella yksikkoympyraa,
# H(z) = (1 - z^-1) / (1 - a z^-1). Lovi on noin (1 - a) fs / (2 pi) leve.
a = 0.999
y = signal.lfilter([1.0, -1.0], [1.0, -a], x)
dc, s = tasot(y[n // 2:])                 # alkutransientti pois
print(f"jalkeen: tasakomponentti {dc:4.0f} dB, signaali {s:4.0f} dB, "
      f"lovi {(1 - a) * fs / (2 * np.pi):.0f} Hz")
# @loppu esto

# @alku keskiarvo
# Vaihtoehto: tallenteen keskiarvo. Toimii, jos tasakomponentti ei muutu
# (esim. vahvistuksen saato muuttaa sita).
dc, _ = tasot(x - x.mean())
print(f"keskiarvon vahennys: tasakomponentti {dc:4.0f} dB")
# @loppu keskiarvo
