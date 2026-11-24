"""Tuottaa C-otsakkeen 05-fir/kertoimet.h suunnitellusta suotimesta."""

import numpy as np
from scipy import signal

# @alku generoi
fs, raja, lkm = 8_000.0, 1_000.0, 31
h = signal.firwin(lkm, raja, window=("kaiser", 5.0), fs=fs)
if not np.allclose(h, h[::-1], rtol=0.0, atol=0.0):
    raise SystemExit("odotettiin symmetrista suodinta")

print("// Generoitu: python3 05-kertoimet.py > 05-fir/kertoimet.h")
print(f"// firwin({lkm}, {raja:g} Hz, kaiser 5.0, fs = {fs:g} Hz)")
print("#pragma once")
print(f"#define KERTOIMIA {lkm}")
print("static const double kertoimet[KERTOIMIA] = {")
# 12 merkitsevaa numeroa: pyoristysvirhe on noin 240 dB signaalin alla,
# eika tulos riipu viimeisista biteista, jotka voivat vaihdella koneittain.
h = np.where(np.abs(h) < 1e-15, 0.0, h)          # ei -1e-18-roskaa
for i in range(0, lkm, 4):
    print("    " + " ".join(f"{float(c):.12g}," for c in h[i:i + 4]))
print("};")
# @loppu generoi
