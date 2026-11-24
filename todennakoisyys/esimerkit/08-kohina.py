"""Kohina: SNR desibeleinä ja keskiarvoistuksen hyöty."""

import math

import numpy as np

rng = np.random.default_rng(31)

# @alku snr
# Anturi: tasajännite 1.0 V ja valkoinen kohina, keskihajonta 0.1 V.
signaali, sigma = 1.0, 0.1
n = 100_000
mittaus = signaali + rng.normal(0.0, sigma, n)
kohina = mittaus - signaali
snr = signaali**2 / float(np.mean(kohina**2))
print(f"SNR = {snr:.1f} = {10 * math.log10(snr):.2f} dB"
      f" (teoria {20 * math.log10(signaali / sigma):.2f} dB)")
# @loppu snr

# @alku keskiarvoistus
# N mittauksen keskiarvo: kohinan keskihajonta pienenee sqrt(N):llä,
# SNR paranee 10 log10(N) dB.
for N in (1, 4, 16, 64):
    ka = mittaus[: (n // N) * N].reshape(-1, N).mean(axis=1)
    s = float(ka.std())
    print(f"N = {N:2}: hajonta {s:.4f} V (teoria {sigma / math.sqrt(N):.4f}),"
          f" SNR {20 * math.log10(signaali / s):5.2f} dB")
# @loppu keskiarvoistus
