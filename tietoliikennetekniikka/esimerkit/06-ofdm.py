"""OFDM pienessä mittakaavassa: QPSK, IFFT, syklinen etuliite ja
yhden kertoimen taajuustason korjain monitiekanavassa."""

import numpy as np
import numpy.typing as npt

Kompleksi = npt.NDArray[np.complex128]

ALIKANTOJA = 64
ETULIITE = 16
rng = np.random.default_rng(5)


def qpsk(bitit: npt.NDArray[np.int64]) -> Kompleksi:
    symbolit = ((1 - 2 * bitit[0::2]) + 1j * (1 - 2 * bitit[1::2]))
    return np.asarray(symbolit / np.sqrt(2), dtype=np.complex128)


def bitit_qpsk(symbolit: Kompleksi) -> npt.NDArray[np.int64]:
    tulos = np.empty(2 * len(symbolit), dtype=np.int64)
    tulos[0::2] = symbolit.real < 0
    tulos[1::2] = symbolit.imag < 0
    return tulos


# @alku ofdm
def siirto(etuliite: int, snr_db: float, symboleita: int = 200) -> float:
    """Palauttaa bittivirhesuhteen."""
    kanava = np.array([1.0, 0, 0, 0.7, 0, 0.5j])     # monitie: 6 tappia
    bitit = rng.integers(0, 2, 2 * ALIKANTOJA * symboleita)
    taajuustaso = qpsk(bitit).reshape(symboleita, ALIKANTOJA)
    aikataso = np.fft.ifft(taajuustaso, axis=1)
    lahetys = np.hstack([aikataso[:, ALIKANTOJA - etuliite:], aikataso])
    vastaanotto = np.convolve(lahetys.ravel(), kanava)[:lahetys.size]
    teho = np.mean(np.abs(vastaanotto) ** 2)
    kohina = np.sqrt(teho / 10 ** (snr_db / 10) / 2) * (
        rng.standard_normal(vastaanotto.size)
        + 1j * rng.standard_normal(vastaanotto.size))
    vastaanotto = (vastaanotto + kohina).reshape(symboleita, -1)
    vastaanotto = vastaanotto[:, etuliite:]          # etuliite pois
    arvio = np.fft.fft(vastaanotto, axis=1)
    arvio /= np.fft.fft(kanava, ALIKANTOJA)          # 1-tap-korjain
    virheita = np.count_nonzero(bitit_qpsk(arvio.ravel()) != bitit)
    return virheita / bitit.size
# @loppu ofdm


for etuliite in (0, ETULIITE):
    for snr in (15.0, 30.0):
        ber = siirto(etuliite, snr)
        print(f"etuliite {etuliite:>2}, SNR {snr:4.0f} dB:"
              f" bittivirheitä {ber:7.2%}")
