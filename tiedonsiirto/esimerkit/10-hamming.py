"""Hamming(7,4) AWGN-kanavassa: kova ja pehmeä päätös, koodausvahvistus."""

import itertools

import numpy as np
from scipy.special import erfc

rng = np.random.default_rng(16)

# @alku koodi
G = np.array([[1, 0, 0, 0, 1, 1, 0],          # generaattorimatriisi [I | P]
              [0, 1, 0, 0, 1, 0, 1],
              [0, 0, 1, 0, 0, 1, 1],
              [0, 0, 0, 1, 1, 1, 1]])
viestit = np.array(list(itertools.product([0, 1], repeat=4)))
koodisanat = viestit @ G % 2                  # kaikki 16 koodisanaa
etaisyydet = koodisanat.sum(axis=1)[1:]
print(f"pienin etäisyys {etaisyydet.min()}, korjaa"
      f" {(etaisyydet.min() - 1) // 2} virheen")
# @loppu koodi

# @alku dekooderit
x = 1.0 - 2 * koodisanat                      # BPSK: 0 -> +1, 1 -> -1


def kova(r: np.ndarray) -> np.ndarray:
    """Bitit päätöksiksi, sitten lähin koodisana Hamming-etäisyydellä."""
    bitit = (r < 0).astype(int)
    d = (bitit[:, None, :] != koodisanat[None, :, :]).sum(axis=2)
    return viestit[np.argmin(d, axis=1)]


def pehmea(r: np.ndarray) -> np.ndarray:
    """Lähin koodisana euklidisesti eli suurin korrelaatio näytteisiin."""
    return viestit[np.argmax(r @ x.T, axis=1)]
# @loppu dekooderit


# @alku vertailu
R = 4 / 7
print("Eb/N0   koodaamaton   kova       pehmeä")
for EbN0_dB in (3.0, 5.0, 7.0):
    EbN0 = 10 ** (EbN0_dB / 10)
    lohkoja = 100_000
    u = rng.integers(0, 16, lohkoja)
    # Sama energia tietobittiä kohti: koodibitin energia on R * Eb.
    sigma = np.sqrt(1 / (2 * R * EbN0))
    r = x[u] + sigma * rng.standard_normal((lohkoja, 7))
    ber = [float(np.mean(f(r) != viestit[u])) for f in (kova, pehmea)]
    koodaamaton = 0.5 * erfc(np.sqrt(EbN0))
    print(f"{EbN0_dB:4.0f} dB   {koodaamaton:9.2e}  {ber[0]:9.2e}"
          f"  {ber[1]:9.2e}")
# @loppu vertailu
