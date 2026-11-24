"""Gray- ja binäärijärjestys 16-QAM:ssa: sama symbolivirhe, eri BER."""

import numpy as np

rng = np.random.default_rng(4)

# @alku vertailu
# Pisteet ovat samat; vain bittien nimiöt (akselin tasoille) eroavat.
tasot = np.array([-3, -1, 1, 3]) / np.sqrt(10)    # keskienergia 1
pisteet = (tasot[:, None] + 1j * tasot[None, :]).ravel()   # indeksi 4i + q
nimiot = {"Gray": [0, 1, 3, 2], "binääri": [0, 1, 2, 3]}

n = 200_000
lahetetty = rng.integers(0, 16, n)            # pisteen indeksi
EsN0_dB = 14.0
N0 = 10 ** (-EsN0_dB / 10)
kohina = np.sqrt(N0 / 2) * (rng.standard_normal(n)
                            + 1j * rng.standard_normal(n))
vastaanotettu = pisteet[lahetetty] + kohina
etaisyys = np.abs(vastaanotettu[:, None] - pisteet[None, :])
ilmaistu = np.argmin(etaisyys, axis=1)       # lähin piste
ser = np.mean(ilmaistu != lahetetty)
for nimi, koodi in nimiot.items():
    nimio = np.array([(koodi[k // 4] << 2) | koodi[k % 4] for k in range(16)])
    erot = nimio[lahetetty] ^ nimio[ilmaistu]
    bittivirheet = sum(bin(int(e)).count("1") for e in erot)
    print(f"{nimi:8s} SER {ser:.4f}  BER {bittivirheet / (4 * n):.5f}"
          f"  bittivirheitä/symbolivirhe {bittivirheet / (ser * n):.2f}")
# @loppu vertailu
