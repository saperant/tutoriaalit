"""Aliasointi kuultavana: taajuuspyyhkäisy Nyquistin taajuuden yli."""

import wave
from pathlib import Path

import numpy as np
import numpy.typing as npt

Jono = npt.NDArray[np.float64]


def kirjoita_wav(polku: Path, x: Jono, fs: int) -> None:
    """16-bittinen mono-WAV standardikirjaston wave-moduulilla."""
    naytteet = np.round(0.5 * x * 32767).astype("<i2")
    with wave.open(str(polku), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(fs)
        w.writeframes(naytteet.tobytes())


# @alku pyyhkaisy
fs = 8_000                                # Nyquistin taajuus 4 kHz
kesto, f_loppu = 7.0, 7_000.0             # taajuus nousee 1 kHz sekunnissa
t = np.arange(int(kesto * fs)) / fs
vaihe = np.pi * (f_loppu / kesto) * t**2  # taajuus hetkellä t: 1000 t
x = np.sin(vaihe)                         # näytteistetään ilman suodatusta
kirjoita_wav(Path("pyyhkaisy.wav"), x, fs)

print(" aika   todellinen   näytteistä mitattu")
for hetki in [1.0, 3.0, 3.5, 5.0, 6.5]:
    alku = int(hetki * fs) - 128
    pala = x[alku:alku + 256] * np.hanning(256)
    huippu = np.argmax(np.abs(np.fft.rfft(pala, n=4_096)))
    mitattu = huippu * fs / 4_096
    print(f"{hetki:4.1f} s {1_000 * hetki:9.0f} Hz {mitattu:14.0f} Hz")
# @loppu pyyhkaisy
