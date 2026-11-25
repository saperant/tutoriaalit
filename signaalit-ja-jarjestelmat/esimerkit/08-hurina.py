"""Lovisuodin kuultavana: sävelet ja verkkohurina ennen ja jälkeen."""

import wave
from pathlib import Path

import numpy as np
import numpy.typing as npt
from scipy import signal

Jono = npt.NDArray[np.float64]


def kirjoita_wav(polku: Path, x: Jono, fs: int) -> None:
    naytteet = np.round(np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(polku), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(fs)
        w.writeframes(naytteet.tobytes())


def taso_db(x: Jono, f: float, fs: int) -> float:
    """Taajuuden f komponentin amplitudi desibeleinä (korrelaatio)."""
    n = np.arange(len(x))
    osoitin = 2 * np.mean(x * np.exp(-2j * np.pi * f / fs * n))
    return float(20 * np.log10(abs(osoitin) + 1e-12))


# @alku hurina
fs = 8_000
t = np.arange(3 * fs) / fs
savelet = np.zeros_like(t)
for i, f in enumerate([330.0, 440.0, 550.0]):      # sekunti kutakin
    osa = slice(i * fs, (i + 1) * fs)
    savelet[osa] = 0.3 * np.sin(2 * np.pi * f * t[osa]) * np.hanning(fs)
hurina = 0.3 * np.sin(2 * np.pi * 50 * t)
b, a = signal.iirnotch(50.0, Q=10.0, fs=fs)        # lovi 50 Hz, leveys 5 Hz
puhdistettu = signal.lfilter(b, a, savelet + hurina)
kirjoita_wav(Path("ennen.wav"), savelet + hurina, fs)
kirjoita_wav(Path("jalkeen.wav"), puhdistettu, fs)

loppu = slice(fs, 3 * fs)                          # asettumisen jälkeen
ennen = taso_db((savelet + hurina)[loppu], 50, fs)
jalkeen = taso_db(puhdistettu[loppu], 50, fs)
print(f"50 Hz:n hurina ennen {ennen:.1f} dB, jälkeen alle -100 dB:",
      jalkeen < -100)
keski = slice(fs + fs // 4, 2 * fs - fs // 4)      # 440 Hz:n keskiosa
muutos = (taso_db(puhdistettu[keski], 440, fs)
          - taso_db(savelet[keski], 440, fs))
print(f"440 Hz:n sävelen muutos {round(muutos, 2) + 0.0:.2f} dB")
# @loppu hurina
