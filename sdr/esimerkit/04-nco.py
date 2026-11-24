"""NCO: vaiheakkumulaattori, taulukko ja vaiheen katkaisun harhalahdot."""

import numpy as np

fs = 912e3


# @alku nco
def nco(taajuus: float, n: int, taulukkobitit: int) -> np.ndarray:
    """32 bitin akkumulaattori; taulukon osoitteena ylimmat bitit.

    Askel = round(f / fs * 2^32). Akkumulaattori vuotaa yli tahallaan:
    2^32 vastaa taytta kierrosta."""
    askel = round(taajuus / fs * 2**32) & 0xFFFFFFFF
    vaihe = (np.arange(n, dtype=np.uint64) * askel) & 0xFFFFFFFF
    taulukko = np.exp(2j * np.pi * np.arange(2**taulukkobitit)
                      / 2**taulukkobitit)
    tulos: np.ndarray = taulukko[vaihe >> (32 - taulukkobitit)]
    return tulos
# @loppu nco


# @alku resoluutio
print(f"taajuusresoluutio fs / 2^32 = {fs / 2**32 * 1e3:.3f} mHz")
haluttu = 123_456.7
askel = round(haluttu / fs * 2**32)
print(f"{haluttu} Hz: askel {askel}, todellinen "
      f"{askel * fs / 2**32:.4f} Hz")
# @loppu resoluutio

# @alku sfdr
n = 1 << 16
for bitit in (8, 10, 12):
    z = nco(haluttu, n, bitit)
    S = np.abs(np.fft.fft(z * np.blackman(n)))
    paa = int(np.argmax(S))
    muut = np.delete(S, range(paa - 8, paa + 9))
    sfdr = 20 * np.log10(S[paa] / muut.max())
    print(f"taulukko 2^{bitit}: SFDR {sfdr:5.1f} dBc "
          f"(nyrkkisaanto 6,02 x {bitit} = {6.02 * bitit:5.1f} dB)")
# @loppu sfdr
