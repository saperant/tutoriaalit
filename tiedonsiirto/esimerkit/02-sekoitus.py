"""Kantataajuus ja kaistanpäästö: sekoitus ylös ja alas sekä verhokäyrä."""

import numpy as np
from scipy import signal

# @alku ylos
fs, fc = 100_000.0, 10_000.0
t = np.arange(20_000) / fs
i_haara = np.cos(2 * np.pi * 500 * t)         # I: samavaiheinen
q_haara = 0.5 * np.sin(2 * np.pi * 1_200 * t)  # Q: kvadratuuri
kanta = i_haara + 1j * q_haara                # kompleksinen verhokäyrä
kantoaalto = np.exp(2j * np.pi * fc * t)
kaista = np.real(kanta * kantoaalto)          # = I cos - Q sin, reaalinen
# @loppu ylos


# @alku spektri
def huiput(x: np.ndarray, lkm: int) -> list[float]:
    """Suurimpien spektriviivojen taajuudet kilohertseinä, nousevasti."""
    X = np.abs(np.fft.fftshift(np.fft.fft(x)))
    f = np.fft.fftshift(np.fft.fftfreq(len(x), 1 / fs))
    return sorted(round(float(v) / 1e3, 1) for v in f[np.argsort(X)[-lkm:]])


print("kantataajuus/kHz: ", huiput(kanta, 4))
print("kaistanpäästö/kHz:", huiput(kaista, 8))
# @loppu spektri

# @alku alas
# Sekoitus alas: kerro 2 e^{-j 2 pi fc t} ja suodata pois 2 fc:n kuva.
alipaasto = signal.firwin(201, 3_000.0, fs=fs)
sekoitettu = 2 * kaista * np.conj(kantoaalto)
palautettu = signal.filtfilt(alipaasto, [1.0], sekoitettu)
keski = slice(1_000, -1_000)                  # reunat ohi
virhe = np.max(np.abs(palautettu[keski] - kanta[keski]))
print(f"I ja Q takaisin, suurin virhe {virhe:.4f}")
# @loppu alas

# @alku verho
# Kaistanpäästösignaalin verhokäyrä on kantataajuussignaalin itseisarvo.
analyyttinen = signal.hilbert(kaista)
ero = np.max(np.abs(np.abs(analyyttinen[keski]) - np.abs(kanta[keski])))
print(f"verhokäyrä |kanta| = |hilbert(kaista)|, suurin ero {ero:.4f}")
teho_kanta = np.mean(np.abs(kanta) ** 2)
teho_kaista = np.mean(kaista**2)
print(f"teho: kanta {teho_kanta:.4f}, kaista {teho_kaista:.4f}")
# @loppu verho
