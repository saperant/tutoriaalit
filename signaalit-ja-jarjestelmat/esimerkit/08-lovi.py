"""50 Hz:n verkkohäiriön poisto lovisuotimella."""

import numpy as np
from scipy import signal

# @alku lovi
fs = 500.0
f0 = 50.0
w0 = 2 * np.pi * f0 / fs
r = 0.98                                      # napojen säde: loven leveys
nollat = [np.exp(1j * w0), np.exp(-1j * w0)]
navat = [r * np.exp(1j * w0), r * np.exp(-1j * w0)]
b, a = signal.zpk2tf(nollat, navat, 1.0)
b, a = b.real, a.real
_, H1 = signal.freqz(b, a, worN=[0.0], fs=fs)
b = b / abs(H1[0])                            # vahvistus 1 tasajännitteelle

f, H = signal.freqz(b, a, worN=[0.0, 10.0, 45.0, 49.0, 50.0, 51.0,
                                55.0, 100.0], fs=fs)
print("  f/Hz   vahvistus/dB")
for fi, Hi in zip(f, H, strict=True):
    if abs(Hi) < 1e-6:
        print(f"{fi:6.0f}   alle -120")    # nolla yksikköympyrällä
        continue
    db = round(20 * np.log10(abs(Hi)), 2) + 0.0
    print(f"{fi:6.0f} {db:10.2f}")
b2, a2 = signal.iirnotch(f0, Q=f0 / (fs * (1 - r) / np.pi), fs=fs)
samat = np.allclose(np.sort_complex(np.roots(a2)),
                    np.sort_complex(np.roots(a)), atol=1e-3)
print("iirnotch(50, Q) antaa samat navat:", bool(samat))
# @loppu lovi

# @alku kayttoon
t = np.arange(5_000) / fs
ekg = np.sin(2 * np.pi * 1.2 * t) ** 31        # terävä sykepiikki 1.2 Hz
hurina = 0.5 * np.sin(2 * np.pi * 50 * t + 0.4)
y = signal.lfilter(b, a, ekg + hurina)
virhe_ennen = np.sqrt(np.mean(hurina[2500:] ** 2))
virhe_jalkeen = np.sqrt(np.mean((y - ekg)[2500:] ** 2))
print(f"häiriön tehollisarvo {virhe_ennen:.4f} -> {virhe_jalkeen:.4f}")
# @loppu kayttoon
