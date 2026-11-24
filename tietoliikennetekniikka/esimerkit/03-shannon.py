"""Kanavan kapasiteetti: Nyquistin ja Shannonin rajat."""

import math


def shannon(kaista_hz: float, snr_db: float) -> float:
    """Kohinaisen kanavan kapasiteetti C = B · log2(1 + S/N)."""
    return kaista_hz * math.log2(1 + 10 ** (snr_db / 10))


def nyquist(kaista_hz: float, tasoja: int) -> float:
    """Kohinattoman kanavan raja C = 2B · log2(M)."""
    return 2 * kaista_hz * math.log2(tasoja)


# @alku kanavat
kanavat = [
    ("puhelinlinja", 3.1e3, 30.0),
    ("Wi-Fi 20 MHz", 20e6, 25.0),
    ("Wi-Fi 20 MHz, heikko", 20e6, 5.0),
    ("5G 100 MHz", 100e6, 20.0),
]
print(f"{'kanava':<21}{'B (kHz)':>9}{'SNR':>5}{'C (kbit/s)':>12}"
      f"{'bit/s/Hz':>9}")
for nimi, kaista, snr in kanavat:
    c = shannon(kaista, snr)
    print(f"{nimi:<21}{kaista / 1e3:>9.1f}{snr:>5.0f}{c / 1e3:>12.1f}"
          f"{c / kaista:>9.2f}")
# @loppu kanavat

# @alku tasot
# Kuinka monta tasoa tarvitaan, jotta Nyquistin raja yltää Shannonin
# rajaan? Enempää tasoja ei kohinan takia voi erottaa.
kaista, snr = 3.1e3, 30.0
for m in (2, 4, 16, 32, 64):
    print(f"M={m:>2}: Nyquist {nyquist(kaista, m) / 1e3:5.1f} kbit/s")
print(f"Shannon: {shannon(kaista, snr) / 1e3:5.1f} kbit/s")
# @loppu tasot
