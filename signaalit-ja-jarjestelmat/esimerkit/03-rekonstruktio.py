"""Rekonstruktio näytteistä: sinc-interpolointi ja nollannen asteen pito."""

import numpy as np
import numpy.typing as npt

Jono = npt.NDArray[np.float64]


def signaali(t: Jono) -> Jono:
    """Kaistarajoitettu testisignaali: 50 Hz ja 180 Hz."""
    return (np.sin(2 * np.pi * 50 * t)
            + 0.5 * np.cos(2 * np.pi * 180 * t + 0.3))


# @alku sinc
def sinc_interpoloi(naytteet: Jono, fs: float, t: Jono) -> Jono:
    """x(t) = sum x[n] sinc(fs t - n), Whittaker-Shannonin kaava."""
    n = np.arange(len(naytteet))
    return np.asarray(
        np.sinc(fs * t[:, None] - n[None, :]) @ naytteet, dtype=float)


fs = 500.0                                # Nyquist 250 Hz > 180 Hz
naytteet = signaali(np.arange(400) / fs)  # 0.8 s
t = np.linspace(0.3, 0.5, 1001)           # keskiosa, kaukana reunoista
virhe_sinc = np.max(np.abs(sinc_interpoloi(naytteet, fs, t) - signaali(t)))
print(f"sinc-interpolointi: suurin virhe {virhe_sinc:.4f}")
# @loppu sinc

# @alku pito
pito = naytteet[np.floor(t * fs).astype(int)]   # edellinen näyte pidetään
virhe_pito = np.max(np.abs(pito - signaali(t)))
print(f"nollannen asteen pito: suurin virhe {virhe_pito:.4f}")
# Pito vaimentaa taajuutta f kertoimella |sinc(f/fs)|.
for f in (50.0, 180.0, 250.0):
    print(f"  pidon vahvistus {f:3.0f} Hz:lla {abs(np.sinc(f / fs)):.3f}")
# @loppu pito

# @alku liian-harva
fs2 = 300.0                               # Nyquist 150 Hz < 180 Hz
naytteet2 = signaali(np.arange(240) / fs2)
virhe2 = np.max(np.abs(sinc_interpoloi(naytteet2, fs2, t) - signaali(t)))
print(f"fs = {fs2:.0f} Hz: suurin virhe {virhe2:.4f} (180 Hz -> 120 Hz)")
# @loppu liian-harva
