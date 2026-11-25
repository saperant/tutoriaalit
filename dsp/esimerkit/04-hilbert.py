"""Hilbert-muunnin tyypin III FIR:na ja analyyttinen signaali."""

import numpy as np
from scipy import signal

# @alku suunnittelu
fs = 8_000.0
lkm = 63                                    # pariton: tyyppi III
# remez palauttaa kertoimet, joiden vaihe on +90 astetta; Hilbert-
# muuntimen vaihe on -90 astetta, joten merkki kaannetaan.
h = -signal.remez(lkm, [300.0, 3_700.0], [1.0], type="hilbert", fs=fs)
viive = (lkm - 1) // 2                      # kokonainen maara naytteita
f, H = signal.freqz(h, worN=[500.0, 1_000.0, 2_000.0, 3_500.0], fs=fs)
vaihe = np.degrees(np.angle(H * np.exp(2j * np.pi * f / fs * viive)))
print("antisymmetrinen:", np.allclose(h, -h[::-1]))
print("joka toinen kerroin nolla:",
      np.allclose(h[viive % 2::2], 0, atol=1e-3))
for fi, Hi, vi in zip(f, H, vaihe, strict=True):
    print(f"{fi:6.0f} Hz  |H| {abs(Hi):.4f}  vaihe {vi:6.1f} astetta")
# @loppu suunnittelu

# @alku verho
n = np.arange(4_000)
verho = 1.0 + 0.5 * np.sin(2 * np.pi * 20.0 / fs * n)    # hidas viesti
x = verho * np.cos(2 * np.pi * 1_000.0 / fs * n)         # AM-signaali
q = signal.lfilter(h, [1.0], x)                          # 90 astetta
i = np.concatenate([np.zeros(viive), x[:-viive]])        # sama viive
analyyttinen = i + 1j * q
alku = 2 * lkm
arvio = np.abs(analyyttinen)[alku:]
oikea = verho[alku - viive:-viive]
print(f"verhokayran suurin virhe {np.max(np.abs(arvio - oikea)):.4f}")
kulma = np.unwrap(np.angle(analyyttinen[alku:]))
taajuus = np.diff(kulma) * fs / (2 * np.pi)
print(f"hetkellinen taajuus {taajuus.mean():.1f} Hz")
valmis = np.abs(signal.hilbert(x))[alku:-alku]           # FFT-menetelma
print("scipy.signal.hilbert antaa saman verhon:",
      np.allclose(valmis, verho[alku:-alku], atol=1e-2))
# @loppu verho
