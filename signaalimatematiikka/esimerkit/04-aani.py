"""Huojunta kuultavana: kaksi lähes samaa säveltä WAV-tiedostona."""

import wave
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

Taulukko = NDArray[np.float64]


# @alku wav
def kirjoita_wav(polku: Path, x: Taulukko, fs: int) -> None:
    """16-bittinen mono-WAV; näytteet skaalataan välille [-0.8, 0.8]."""
    skaalattu = 0.8 * x / np.max(np.abs(x))
    näytteet = np.round(skaalattu * 32767).astype("<i2")
    with wave.open(str(polku), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(fs)
        w.writeframes(näytteet.tobytes())


fs = 8000
t = np.arange(3 * fs) / fs                       # kolme sekuntia
x = np.cos(2 * np.pi * 440 * t) + np.cos(2 * np.pi * 444 * t)
kirjoita_wav(Path("huojunta.wav"), x, fs)
# @loppu wav

verho = 2 * np.abs(np.cos(np.pi * 4 * t))
keski = verho[1:-1]
hiljaiset = int(np.sum((keski < verho[:-2]) & (keski < verho[2:])))
print(f"huojunta.wav: {len(t) / fs:.0f} s, {fs} Hz, 16 bittiä, mono")
print(f"voimakkuus käy nollassa {hiljaiset} kertaa eli "
      f"{hiljaiset / (len(t) / fs):.0f} kertaa sekunnissa")
