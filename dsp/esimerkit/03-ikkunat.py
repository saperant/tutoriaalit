"""Ikkunan valinta: vaimennus ja siirtymakaistan leveys."""

import numpy as np
from scipy import signal

# @alku vertailu
lkm, fc = 101, 0.25
ikkunat: list[str | tuple[str, float]] = [
    "boxcar", "hann", "hamming", "blackman", ("kaiser", 8.0)]
print("ikkuna       delta     vaimennus  siirtyma*N")
for ikkuna in ikkunat:
    h = signal.firwin(lkm, fc, window=ikkuna, fs=1.0)
    f, H = signal.freqz(h, worN=1 << 17, fs=1.0)
    amp = np.abs(H)
    # Estokaistan suurin sivukeila maarittaa poikkeaman delta; sama
    # poikkeama nakyy paastokaistalla.
    huiput = signal.argrelmax(amp)[0]
    delta = amp[huiput[f[huiput] > fc]].max()
    paasto = f[np.argmax(np.abs(amp - 1) > delta * 1.001)]
    esto = f[np.nonzero(amp > delta * 1.001)[0][-1] + 1]
    nimi = ikkuna if isinstance(ikkuna, str) else f"kaiser {ikkuna[1]:g}"
    print(f"{nimi:12s} {delta:.5f} {-20 * np.log10(delta):6.1f} dB"
          f" {(esto - paasto) * lkm:9.2f}")
# @loppu vertailu
