"""Sointiväri on harmonisten jakauma: sama sävel kolmena aaltomuotona."""

import wave
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

Taulukko = NDArray[np.float64]


def kirjoita_wav(polku: Path, x: Taulukko, fs: int) -> None:
    näytteet = np.round(0.5 * x / np.max(np.abs(x)) * 32767).astype("<i2")
    with wave.open(str(polku), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(fs)
        w.writeframes(näytteet.tobytes())


# @alku sointi
fs, f0 = 16000, 220.0
t = np.arange(2 * fs) / fs
ylin = int(fs / 2 / f0)        # harmoniset alle puolen näytetaajuuden
k = np.arange(1, ylin + 1)[:, np.newaxis]
kertoimet = {
    "sini": np.where(k == 1, 1.0, 0.0),
    "kantti": np.where(k % 2 == 1, 4 / (np.pi * k), 0.0),
    "saha": -2 / (np.pi * k),
}
print(f"sävel {f0:.0f} Hz, harmonisia enintään {ylin}")
for nimi, b in kertoimet.items():
    x = np.sum(b * np.sin(2 * np.pi * f0 * k * t), axis=0)
    kirjoita_wav(Path(f"{nimi}.wav"), x, fs)
    teho = np.sum(b**2) / 2
    osuus = 100 * b[0, 0]**2 / 2 / teho
    print(f"{nimi + '.wav':11s} harmonisia {int(np.sum(b != 0)):2d}, "
          f"perustaajuuden osuus tehosta {osuus:5.1f} %")
# @loppu sointi
