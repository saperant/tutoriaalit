"""ADC:n bittimaara, dynamiikka-alue ja ylikuormitus."""

import numpy as np

fs, n = 2.4e6, 1 << 16
k = np.arange(n)
ikkuna = np.blackman(n)


def adc(x: np.ndarray, bitit: int) -> np.ndarray:
    """Kompleksinen ADC: I ja Q pyoristetaan, taysi skaala +-1 leikataan."""
    porras = 2.0 / 2**bitit

    def kvantisoi(v: np.ndarray) -> np.ndarray:
        tulos: np.ndarray = np.clip(np.round(v / porras) * porras,
                                    -1.0, 1.0 - porras)
        return tulos

    return kvantisoi(x.real) + 1j * kvantisoi(x.imag)


def spektri_db(x: np.ndarray) -> np.ndarray:
    """Tehospektri dBFS:na: taysi skaalan kompleksinen aani on 0 dB."""
    X = np.fft.fft(x * ikkuna) / ikkuna.sum()
    tulos: np.ndarray = 20 * np.log10(np.abs(X) + 1e-20)
    return tulos


def aani(f: float, taso_dbfs: float) -> np.ndarray:
    """Kompleksinen aani FFT:n bin keskelle (ei vuotoa)."""
    binni = round(f / fs * n)
    tulos: np.ndarray = 10 ** (taso_dbfs / 20) * np.exp(
        2j * np.pi * binni * k / n)
    return tulos


# @alku bitit
for bitit in (8, 12, 16):
    x = aani(100e3, -1.0)
    virhe = adc(x, bitit) - x
    sqnr = 10 * np.log10(np.mean(np.abs(x) ** 2) / np.mean(np.abs(virhe)**2))
    print(f"{bitit:2} bittia: SQNR {sqnr:5.1f} dB "
          f"(teoria 6,02 N + 1,76 = {6.02 * bitit + 1.76:5.1f} dB)")
# @loppu bitit

# @alku heikko
# Vahva asema -3 dBFS ja heikko -70 dBFS: nakyyko heikko 8 bitilla?
x = aani(100e3, -3.0) + aani(-300e3, -70.0)
rng = np.random.default_rng(5)
x += 3e-3 * (rng.standard_normal(n) + 1j * rng.standard_normal(n))  # dither
S = spektri_db(adc(x, 8))
heikko = S[round(-300e3 / fs * n)]
lattia = np.median(S)
print(f"8 bit: heikko {heikko:.0f} dBFS, lattia {lattia:.0f} dBFS/bin, "
      f"erotus {heikko - lattia:.0f} dB")
# @loppu heikko

# @alku ylikuorma
for taso in (-6.0, 0.0, 3.0):
    S = spektri_db(adc(aani(100e3, taso), 8))
    oma = round(100e3 / fs * n)
    muut = np.delete(S, range(oma - 8, oma + 9))
    print(f"aani {taso:+4.0f} dBFS: suurin harhalahto {muut.max():6.1f} "
          f"dBFS, SFDR {S[oma] - muut.max():5.1f} dB")
# @loppu ylikuorma
