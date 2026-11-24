"""Ensimmainen suodin: vaatimuksista kertoimiin ja tarkistukseen."""

import numpy as np
from scipy import signal

# @alku vaatimukset
fs = 8_000.0            # naytetaajuus (Hz)
paasto = 1_000.0        # paastokaista 0 ... 1000 Hz
esto = 1_500.0          # estokaista 1500 Hz ... fs/2
vaimennus_db = 60.0     # vaadittu vaimennus estokaistalla
# @loppu vaatimukset

# @alku suunnittelu
siirtyma = (esto - paasto) / (fs / 2)       # 1 = Nyquistin taajuus
lkm, beta = signal.kaiserord(vaimennus_db, siirtyma)
lkm |= 1                                    # pariton pituus (tyyppi I)
h = signal.firwin(lkm, (paasto + esto) / 2, window=("kaiser", beta),
                  fs=fs)
print(f"kertoimia {lkm}, Kaiserin beta {beta:.3f}")
# @loppu suunnittelu

# @alku tarkistus
f, H = signal.freqz(h, worN=16_384, fs=fs)
db = 20 * np.log10(np.maximum(np.abs(H), 1e-12))
kaista = db[f <= paasto]
print(f"0-1000 Hz: aaltoilu {kaista.max() - kaista.min():.4f} dB")
print(f"1500-4000 Hz: vaimennus {-db[f >= esto].max():.1f} dB")
# @loppu tarkistus

# @alku kaytto
rng = np.random.default_rng(1)
n = np.arange(16_000)
puhdas = np.sin(2 * np.pi * 440.0 / fs * n)
hairio = 0.5 * np.sin(2 * np.pi * 2_500.0 / fs * n)
hairio += 0.2 * rng.standard_normal(n.size)
y = signal.lfilter(h, [1.0], puhdas + hairio)
viive = (lkm - 1) // 2                      # ryhmaviive naytteina
alku = 2 * lkm                              # transientti ohi


def snr(arvio: np.ndarray, viite: np.ndarray) -> float:
    virhe = arvio - viite
    return float(10 * np.log10(np.sum(viite**2) / np.sum(virhe**2)))


print(f"SNR ennen {snr((puhdas + hairio)[alku:], puhdas[alku:]):5.1f} dB")
print(f"SNR jalkeen {snr(y[alku:], puhdas[alku - viive:-viive]):5.1f} dB")
# @loppu kaytto
