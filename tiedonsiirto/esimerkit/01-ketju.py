"""Koko siirtoketju pienenä: bitit, QPSK, pulssinmuokkaus, kohina, ilmaisu."""

import numpy as np
import numpy.typing as npt
from scipy.special import erfc

Reaali = npt.NDArray[np.float64]
Kompleksi = npt.NDArray[np.complex128]


# @alku pulssi
def rrc(beta: float, sps: int, janne: int) -> Reaali:
    """Juurikorotettu kosini, jonka energia on 1 (sps näytettä/symboli)."""
    t = np.arange(-janne * sps // 2, janne * sps // 2 + 1) / sps
    h = np.empty_like(t)
    for i, ti in enumerate(t):
        if np.isclose(ti, 0.0):
            h[i] = 1 + beta * (4 / np.pi - 1)
        elif np.isclose(abs(ti), 1 / (4 * beta)):
            h[i] = beta / np.sqrt(2) * (
                (1 + 2 / np.pi) * np.sin(np.pi / (4 * beta))
                + (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta)))
        else:
            h[i] = (np.sin(np.pi * ti * (1 - beta))
                    + 4 * beta * ti * np.cos(np.pi * ti * (1 + beta))) / (
                np.pi * ti * (1 - (4 * beta * ti) ** 2))
    tulos: Reaali = h / np.sqrt(np.sum(h**2))
    return tulos
# @loppu pulssi


# @alku lahetin
rng = np.random.default_rng(1)
sps, beta, janne = 8, 0.35, 10
bitit = rng.integers(0, 2, 200_000)
# QPSK: kaksi bittiä symbolia kohti, Gray-järjestys, energia Es = 1.
symbolit = ((1 - 2 * bitit[0::2]) + 1j * (1 - 2 * bitit[1::2])) / np.sqrt(2)
h = rrc(beta, sps, janne)
nostettu = np.zeros(len(symbolit) * sps, dtype=complex)
nostettu[::sps] = symbolit
lahetetty = np.convolve(nostettu, h)
# @loppu lahetin

# @alku kanava
EbN0_dB = 6.0
N0 = 1.0 / (2 * 10 ** (EbN0_dB / 10))     # Es = 1, Eb = Es / 2
kohina = np.sqrt(N0 / 2) * (rng.standard_normal(len(lahetetty))
                            + 1j * rng.standard_normal(len(lahetetty)))
vastaanotettu = lahetetty + kohina
# @loppu kanava

# @alku vastaanotin
sovitettu = np.convolve(vastaanotettu, h)       # sovitettu suodin
viive = janne * sps                             # kahden suotimen viive
naytteet = sovitettu[viive::sps][: len(symbolit)]
ilmaistut = np.empty_like(bitit)
ilmaistut[0::2] = naytteet.real < 0
ilmaistut[1::2] = naytteet.imag < 0
virheet = int(np.count_nonzero(ilmaistut != bitit))
teoria = 0.5 * erfc(np.sqrt(10 ** (EbN0_dB / 10)))
print(f"bittejä {len(bitit)}, virheitä {virheet}")
print(f"BER simuloitu {virheet / len(bitit):.2e}, teoria {teoria:.2e}")
# @loppu vastaanotin
