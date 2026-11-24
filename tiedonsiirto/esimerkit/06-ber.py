"""Bittivirhesuhde AWGN-kanavassa: simulaatio teoriaa vastaan."""

import numpy as np
import numpy.typing as npt
from scipy.special import erfc

Kompleksi = npt.NDArray[np.complex128]
rng = np.random.default_rng(9)


def Q(x: float) -> float:
    """Normaalijakauman häntätodennäköisyys P(X > x)."""
    return float(0.5 * erfc(x / np.sqrt(2)))


# @alku konstellaatiot
def gray(i: int) -> int:
    return i ^ (i >> 1)


def qam(M: int) -> Kompleksi:
    L = round(np.sqrt(M))
    b = L.bit_length() - 1
    p = np.empty(M, dtype=complex)
    for i in range(L):
        for q in range(L):
            nimio = (gray(i) << b) | gray(q)
            p[nimio] = (2 * i - L + 1) + 1j * (2 * q - L + 1)
    tulos: Kompleksi = p / np.sqrt(np.mean(np.abs(p) ** 2))
    return tulos


def psk(M: int) -> Kompleksi:
    p = np.empty(M, dtype=complex)
    for k in range(M):
        p[gray(k)] = np.exp(2j * np.pi * (k + 0.5) / M)
    return p
# @loppu konstellaatiot


# @alku teoria
def teoria(nimi: str, M: int, EbN0: float) -> float:
    """Gray-koodatun modulaation BER (QAM ja 8-PSK: lähimmät naapurit)."""
    k = np.log2(M)
    if M <= 4:
        return Q(np.sqrt(2 * EbN0))
    if nimi.endswith("PSK"):
        return float(2 / k * Q(np.sqrt(2 * k * EbN0) * np.sin(np.pi / M)))
    return float(4 / k * (1 - 1 / np.sqrt(M))
                 * Q(np.sqrt(3 * k * EbN0 / (M - 1))))
# @loppu teoria


# @alku simuloi
def simuloi(pisteet: Kompleksi, EbN0: float, virheita: int = 400) -> float:
    """Monte Carlo, kunnes virheitä on tarpeeksi (tai 4 M bittiä)."""
    M = len(pisteet)
    k = M.bit_length() - 1
    N0 = 1 / (k * EbN0)                       # Es = 1
    bitteja = vaarin = 0
    while vaarin < virheita and bitteja < 4_000_000:
        nimiot = rng.integers(0, M, 20_000)
        r = pisteet[nimiot] + np.sqrt(N0 / 2) * (
            rng.standard_normal(len(nimiot))
            + 1j * rng.standard_normal(len(nimiot)))
        ilmaistu = np.argmin(np.abs(r[:, None] - pisteet[None, :]), axis=1)
        erot = (nimiot ^ ilmaistu).astype(np.uint8)
        vaarin += int(np.unpackbits(erot).sum())
        bitteja += k * len(nimiot)
    return vaarin / bitteja
# @loppu simuloi


# @alku vertaa
print("modulaatio  Eb/N0    simuloitu    teoria  suhde")
for nimi, pisteet in (("BPSK", np.array([1.0 + 0j, -1.0 + 0j])),
                      ("QPSK", psk(4)), ("8-PSK", psk(8)),
                      ("16-QAM", qam(16)), ("64-QAM", qam(64))):
    for EbN0_dB in (4.0, 8.0):
        EbN0 = 10 ** (EbN0_dB / 10)
        ber = simuloi(pisteet, EbN0)
        odotettu = teoria(nimi, len(pisteet), EbN0)
        print(f"{nimi:10s} {EbN0_dB:4.0f} dB  {ber:10.2e}  {odotettu:8.2e}"
              f"  {ber / odotettu:5.2f}")
# @loppu vertaa
