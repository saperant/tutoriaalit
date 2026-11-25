"""PSK- ja QAM-konstellaatiot Gray-järjestyksessä ja niiden tunnusluvut."""

import numpy as np
import numpy.typing as npt

Kompleksi = npt.NDArray[np.complex128]


# @alku rakenna
def gray(i: int) -> int:
    """Gray-koodi: peräkkäiset luvut eroavat yhdessä bitissä."""
    return i ^ (i >> 1)


def psk(M: int) -> Kompleksi:
    """M-PSK: piste[nimiö] on symboli, jonka bitit ovat nimiö."""
    pisteet = np.empty(M, dtype=complex)
    for k in range(M):
        pisteet[gray(k)] = np.exp(2j * np.pi * k / M)
    if M == 4:
        pisteet *= np.exp(1j * np.pi / 4)     # QPSK akseleiden väliin
    return pisteet


def qam(M: int) -> Kompleksi:
    """Neliö-QAM: kummallakin akselilla sqrt(M) tasoa Gray-järjestyksessä."""
    L = round(np.sqrt(M))
    b = L.bit_length() - 1                    # bittejä akselia kohti
    pisteet = np.empty(M, dtype=complex)
    for i in range(L):
        for q in range(L):
            nimio = (gray(i) << b) | gray(q)
            pisteet[nimio] = (2 * i - L + 1) + 1j * (2 * q - L + 1)
    tulos: Kompleksi = pisteet / np.sqrt(np.mean(np.abs(pisteet) ** 2))
    return tulos
# @loppu rakenna


# @alku tunnusluvut
def gray_kunnossa(pisteet: Kompleksi) -> bool:
    """Eroavatko kaikki lähimmät naapurit täsmälleen yhdessä bitissä?"""
    d = np.abs(pisteet[:, None] - pisteet[None, :])
    dmin = np.min(d[d > 1e-9])
    naapurit = np.argwhere(np.abs(d - dmin) < 1e-9)
    return all(bin(int(a) ^ int(b)).count("1") == 1 for a, b in naapurit)


print("nimi    bittejä  dmin   huippu/keski  Gray")
for nimi, pisteet in (("BPSK", psk(2)), ("QPSK", psk(4)), ("8-PSK", psk(8)),
                      ("16-PSK", psk(16)), ("16-QAM", qam(16)),
                      ("64-QAM", qam(64))):
    d = np.abs(pisteet[:, None] - pisteet[None, :])
    dmin = np.min(d[d > 1e-9])
    huippu = 10 * np.log10(np.max(np.abs(pisteet) ** 2))
    bitit = len(pisteet).bit_length() - 1
    print(f"{nimi:7s} {bitit:5d}  {dmin:6.3f}  {huippu:7.2f} dB"
          f"     {'kyllä' if gray_kunnossa(pisteet) else 'ei'}")
# @loppu tunnusluvut

# @alku kartta
print("16-QAM, nimiöt (I-bitit | Q-bitit):")
pisteet = qam(16)
tasot = np.unique(np.round(pisteet.real, 6))
for q in tasot[::-1]:
    rivi = []
    for i in tasot:
        nimio = int(np.argmin(np.abs(pisteet - (i + 1j * q))))
        rivi.append(f"{nimio >> 2:02b}|{nimio & 3:02b}")
    print("   " + "  ".join(rivi))
# @loppu kartta
