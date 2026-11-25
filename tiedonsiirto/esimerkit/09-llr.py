"""Pehmeät bitit: 16-QAM:n bittikohtaiset log-uskottavuussuhteet (LLR)."""

import numpy as np

rng = np.random.default_rng(21)

tasot = np.array([-3, -1, 1, 3]) / np.sqrt(10)
koodi = [0, 1, 3, 2]                          # Gray-nimiöt akselin tasoille
pisteet = np.empty(16, dtype=complex)
for i in range(4):
    for q in range(4):
        pisteet[(koodi[i] << 2) | koodi[q]] = tasot[i] + 1j * tasot[q]
bitit_pisteessa = (np.arange(16)[:, None] >> np.arange(3, -1, -1)) & 1


# @alku llr
def llr(r: np.ndarray, N0: float) -> np.ndarray:
    """L = ln P(b = 0 | r) - ln P(b = 1 | r) jokaiselle 4 bitille.

    Tarkka muoto summaa kaikki pisteet (log-sum-exp). Max-log-likiarvo
    käyttäisi vain lähintä pistettä kummastakin joukosta.
    """
    metriikka = -np.abs(r[:, None] - pisteet[None, :]) ** 2 / N0
    tulos = np.empty((len(r), 4))
    for j in range(4):
        nollat = metriikka[:, bitit_pisteessa[:, j] == 0]
        ykkoset = metriikka[:, bitit_pisteessa[:, j] == 1]
        tulos[:, j] = (np.logaddexp.reduce(nollat, axis=1)
                       - np.logaddexp.reduce(ykkoset, axis=1))
    return tulos
# @loppu llr


# @alku kalibrointi
n, EsN0_dB = 200_000, 10.0
N0 = 10 ** (-EsN0_dB / 10)
nimiot = rng.integers(0, 16, n)
r = pisteet[nimiot] + np.sqrt(N0 / 2) * (rng.standard_normal(n)
                                         + 1j * rng.standard_normal(n))
L = llr(r, N0).ravel()
lahetetty = bitit_pisteessa[nimiot].ravel()
vaarin = (L < 0) != (lahetetty == 1)          # kova päätös = LLR:n merkki
print(f"kova päätös LLR:n merkistä: BER {np.mean(vaarin):.4f}")
print("|L|          bittejä   virheosuus   odotettu 1/(1 + e^|L|)")
for ala, yla in ((0, 1), (1, 2), (2, 4), (4, 8), (8, np.inf)):
    osa = (np.abs(L) >= ala) & (np.abs(L) < yla)
    odotettu = np.mean(1 / (1 + np.exp(np.abs(L[osa]))))
    print(f"{ala:2.0f} ... {yla:3.0f}  {osa.sum():8d}"
          f"   {np.mean(vaarin[osa]):10.4f}   {odotettu:8.4f}")
# @loppu kalibrointi
