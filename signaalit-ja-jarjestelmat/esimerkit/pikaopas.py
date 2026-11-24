"""Pikaoppaan SciPy-reseptit: suodatus, analyysi ja spektri."""

import numpy as np
from scipy import signal

fs = 1_000.0
x = np.random.default_rng(0).normal(size=4_000)

# @alku suodatus
b, a = signal.butter(4, 100.0, fs=fs)          # siirtofunktio (b, a)
y = signal.lfilter(b, a, x)                    # kausaalinen suodatus
sos = signal.butter(4, 100.0, fs=fs, output="sos")
y2 = signal.sosfilt(sos, x)                    # sama, numeerisesti vakaa
y3 = signal.filtfilt(b, a, x)                  # nollavaihe, ei kausaalinen
zi = signal.lfilter_zi(b, a) * x[0]            # alku tasapainosta
y4, tila = signal.lfilter(b, a, x[:100], zi=zi)  # lohko ja uusi tila
# @loppu suodatus

# @alku analyysi
z, p, k = signal.tf2zpk(b, a)                  # nollat, navat, vahvistus
stabiili = bool(np.all(np.abs(p) < 1))
f, H = signal.freqz(b, a, worN=[50.0, 100.0, 200.0], fs=fs)
_, gd = signal.group_delay((b, a), w=[50.0], fs=fs)
h = signal.lfilter(b, a, np.r_[1.0, np.zeros(63)])   # impulssivaste
# @loppu analyysi

# @alku spektri
F = np.fft.rfft(x * signal.get_window("hann", len(x)))
fk = np.fft.rfftfreq(len(x), d=1 / fs)         # välin k taajuus k fs/N
fw, P = signal.welch(x, fs=fs, nperseg=512)    # tehospektri, V^2/Hz
xd = signal.decimate(x, 4, ftype="fir")        # suodatus + harvennus
c = signal.fftconvolve(x, h)                   # pitkä konvoluutio
# @loppu spektri

print("sos == ba:", bool(np.allclose(y, y2)), " stabiili:", stabiili)
db = np.round(20 * np.log10(np.abs(H)), 1) + 0.0
print("|H| dB:", " ".join(f"{v:.1f}" for v in db),
      f" ryhmäviive 50 Hz: {gd[0]:.2f} näytettä")
print(f"pituudet: F {len(F)}, P {len(P)}, xd {len(xd)}, c {len(c)},"
      f" y3 {len(y3)}, y4 {len(y4)}")
print(f"nollia {len(z)}, k {k:.2e}")
print(f"fk[1] = {fk[1]:.2f} Hz, fw[1] = {fw[1]:.3f} Hz,"
      f" tila {len(tila)} lukua")
