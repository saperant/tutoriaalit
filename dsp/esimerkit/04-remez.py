"""Parks-McClellan: tasavarahtelyinen suodin ja lyhyin pituus."""

import math

import numpy as np
from scipy import signal

fs, paasto, esto = 8_000.0, 1_000.0, 1_500.0
aaltoilu_db, vaimennus_db = 0.1, 60.0

# @alku painot
# Sallitut poikkeamat lineaarisina: paastokaistan delta_p, eston delta_s.
dp = (10 ** (aaltoilu_db / 20) - 1) / (10 ** (aaltoilu_db / 20) + 1)
ds = 10 ** (-vaimennus_db / 20)
paino = [1.0, dp / ds]               # virhe painotetaan sallitun mukaan
arvio = math.ceil((-20 * math.log10(math.sqrt(dp * ds)) - 13)
                  / (14.6 * (esto - paasto) / fs)) + 1
print(f"delta_p {dp:.5f}, delta_s {ds:.5f}, paino {paino[1]:.1f}")
print(f"pituusarvio {arvio}")
# @loppu painot


# @alku etsi
def mitat(h: np.ndarray) -> tuple[float, float]:
    f, H = signal.freqz(h, worN=1 << 15, fs=fs)
    db = 20 * np.log10(np.abs(H))
    kaista = db[f <= paasto]
    return float(kaista.max() - kaista.min()), float(-db[f >= esto].max())


lkm = arvio - 4
while True:
    h = signal.remez(lkm, [0, paasto, esto, fs / 2], [1, 0], weight=paino,
                     fs=fs)
    aaltoilu, vaimennus = mitat(h)
    if aaltoilu <= aaltoilu_db and vaimennus >= vaimennus_db:
        break
    lkm += 1
print(f"remez: N = {lkm}, aaltoilu {aaltoilu:.3f} dB,"
      f" vaimennus {vaimennus:.1f} dB")
# @loppu etsi

# @alku tasavarahtely
f, H = signal.freqz(h, worN=1 << 15, fs=fs)
A = np.abs(H)
huiput = signal.argrelmax(A)[0]
esto_huiput = A[huiput[f[huiput] > esto]]
print(f"estokaistan huippuja {esto_huiput.size}, suurin/pienin"
      f" {esto_huiput.max() / esto_huiput.min():.3f}")
# @loppu tasavarahtely
