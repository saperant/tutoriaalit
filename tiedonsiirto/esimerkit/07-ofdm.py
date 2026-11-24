"""OFDM: IFFT, syklinen etuliite ja yhden kertoimen taajuuskorjaus."""

import numpy as np

rng = np.random.default_rng(11)
N = 64                                        # alikantoaaltoja
kanava = np.array([0.8, 0, 0.5, 0.3j, 0, 0, 0.2, 0.1])   # monitie, 8 näytettä


def qpsk(n: int) -> np.ndarray:
    b = rng.integers(0, 2, (2, n))
    s: np.ndarray = ((1 - 2 * b[0]) + 1j * (1 - 2 * b[1])) / np.sqrt(2)
    return s


# @alku lahetin
def ofdm_lahetin(data: np.ndarray, cp: int) -> np.ndarray:
    """data: (symbolit, N). IFFT ja syklinen etuliite symbolin eteen."""
    aika = np.fft.ifft(data, axis=1) * np.sqrt(N)  # teho säilyy
    return np.hstack([aika[:, N - cp:], aika]).ravel()


def ofdm_vastaanotin(r: np.ndarray, cp: int, symboleja: int) -> np.ndarray:
    """Poista etuliite ja tee FFT: jokainen alikantoaalto erikseen."""
    lohkot = r[: symboleja * (N + cp)].reshape(symboleja, N + cp)[:, cp:]
    tulos: np.ndarray = np.fft.fft(lohkot, axis=1) / np.sqrt(N)
    return tulos
# @loppu lahetin


# @alku kanava
symboleja = 400
data = qpsk(symboleja * N).reshape(symboleja, N)
H = np.fft.fft(kanava, N)                     # kanavan taajuusvaste
print(f"|H| alikantoaalloilla: {20 * np.log10(np.abs(H).min()):.1f}"
      f" ... {20 * np.log10(np.abs(H).max()):.1f} dB")
for cp in (0, 4, 8, 16):
    lahetetty = ofdm_lahetin(data, cp)
    r = np.convolve(lahetetty, kanava)[: len(lahetetty)]
    r += 10 ** (-30 / 20) * (rng.standard_normal(len(r))
                             + 1j * rng.standard_normal(len(r))) / np.sqrt(2)
    Y = ofdm_vastaanotin(r, cp, symboleja)
    tasattu = Y / H                           # kerroin per alikantoaalto
    virheet = np.count_nonzero(
        (np.sign(tasattu.real) != np.sign(data.real))
        | (np.sign(tasattu.imag) != np.sign(data.imag)))
    evm = np.sqrt(np.mean(np.abs(tasattu - data) ** 2))
    hyoty = N / (N + cp)
    print(f"CP {cp:2d}: symbolivirheitä {virheet:5d} / {data.size},"
          f" EVM {100 * evm:5.1f} %, tehokkuus {100 * hyoty:.0f} %")
# @loppu kanava

# @alku papr
# Monen alikantoaallon summa on lähes normaalijakautunut: huippuja tulee.
ofdm = ofdm_lahetin(qpsk(2_000 * N).reshape(2_000, N), 0)
for raja_dB in (4.0, 8.0, 10.0):
    osuus = np.mean(np.abs(ofdm) ** 2 > 10 ** (raja_dB / 10))
    print(f"OFDM: teho > keskiteho + {raja_dB:4.1f} dB {100 * osuus:7.3f} %"
          f" näytteistä")
# @loppu papr
