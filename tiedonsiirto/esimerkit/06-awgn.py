"""Kohinan kalibrointi: Eb/N0, Es/N0 ja SNR sekä niiden mittaaminen."""

import numpy as np

rng = np.random.default_rng(8)


# @alku muunnokset
def kohinaa(n: int, N0: float) -> np.ndarray:
    """Kompleksista valkoista kohinaa: N0/2 kumpaankin komponenttiin."""
    z: np.ndarray = np.sqrt(N0 / 2) * (rng.standard_normal(n)
                                       + 1j * rng.standard_normal(n))
    return z


bitteja, sps = 4, 8                           # 16-QAM, 8 näytettä/symboli
print("Eb/N0   Es/N0   SNR/näyte   mitattu Es/N0")
for EbN0_dB in (4.0, 10.0):
    EsN0_dB = EbN0_dB + 10 * np.log10(bitteja)
    # Pulssin energia on 1 ja se jakautuu sps näytteelle: signaalin teho
    # näytettä kohti on Es/sps, kohinan N0. SNR näytettä kohti on siis
    # Es/N0 - 10 log10(sps): suodattamaton signaali näyttää huonommalta.
    snr_naytteella = EsN0_dB - 10 * np.log10(sps)
# @loppu muunnokset

# @alku mittaus
    # Mitataan Es/N0 vastaanottimen päätöshetken näytteistä: EVM.
    tasot = np.array([-3, -1, 1, 3]) / np.sqrt(10)
    s = rng.choice(tasot, 50_000) + 1j * rng.choice(tasot, 50_000)
    r = s + kohinaa(len(s), 10 ** (-EsN0_dB / 10))
    evm = np.sqrt(np.mean(np.abs(r - s) ** 2) / np.mean(np.abs(s) ** 2))
    print(f"{EbN0_dB:5.1f}   {EsN0_dB:5.2f}   {snr_naytteella:9.2f}"
          f"   {-20 * np.log10(evm):13.2f}   (EVM {100 * evm:.1f} %)")
# @loppu mittaus
