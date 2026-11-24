"""Kanavan valinta: yksi- ja kaksivaiheinen desimointi 2,4 MS/s -> 48 kS/s."""

import numpy as np
from scipy import signal

FS = 2.4e6
PAASTO, ESTO, VAIMENNUS = 12.5e3, 24e3, 70.0   # kapea kanava, 70 dB


# @alku suunnittelu
def suunnittele(fs: float, paasto: float, esto: float) -> np.ndarray:
    """Kaiserin ikkunalla mitoitettu alipaasto (scipy.signal.kaiserord)."""
    pituus, beta = signal.kaiserord(VAIMENNUS, (esto - paasto) / (fs / 2))
    pituus |= 1                                   # pariton: tyyppi I
    h: np.ndarray = signal.firwin(pituus, (paasto + esto) / 2,
                                  window=("kaiser", beta), fs=fs)
    return h


# Yksi vaihe: siirtymakaista 12,5 -> 24 kHz suoraan 2,4 MS/s:lla.
yksi = [(suunnittele(FS, PAASTO, ESTO), 50)]
# Kaksi vaihetta: 2,4 M -> 240 k (D = 10), sitten 240 k -> 48 k (D = 5).
# Ensimmaisen vaiheen estokaista alkaa vasta 240 k - 24 k = 216 kHz:sta,
# koska vain sinne osuvat taajuudet laskostuvat lopulliselle kaistalle.
kaksi = [(suunnittele(FS, PAASTO, 240e3 - ESTO), 10),
         (suunnittele(FS / 10, PAASTO, ESTO), 5)]
# @loppu suunnittelu


# @alku kustannus
def kertolaskut(vaiheet: list[tuple[np.ndarray, int]]) -> float:
    """Kertolaskuja tulonaytetta kohti, kun vain joka D:s lahto lasketaan."""
    summa, kerroin = 0.0, 1.0
    for h, d in vaiheet:
        summa += len(h) / d / kerroin
        kerroin *= d
    return summa


for nimi, vaiheet in (("yksi vaihe", yksi), ("kaksi vaihetta", kaksi)):
    pituudet = " + ".join(str(len(h)) for h, _ in vaiheet)
    print(f"{nimi:15}: kertoimia {pituudet:9}, "
          f"{kertolaskut(vaiheet):5.1f} kertolaskua/nayte")
# @loppu kustannus

# @alku tarkistus
# Hyotykanava 5 kHz:ssa ja hairitsija 40 kHz:ssa: hairitsijan pitaa
# vaimeta 70 dB eika saa laskostua kanavalle.
n = np.arange(round(0.05 * FS))
x = (np.exp(2j * np.pi * 5e3 * n / FS)
     + 100 * np.exp(2j * np.pi * 40e3 * n / FS))     # 40 dB vahvempi
for nimi, vaiheet in (("yksi vaihe", yksi), ("kaksi vaihetta", kaksi)):
    y = x
    for h, d in vaiheet:
        y = signal.upfirdn(h, y, down=d)
    y = y[len(y) // 4: -len(y) // 4]
    Y = np.abs(np.fft.fft(y * np.blackman(len(y))))
    f = np.fft.fftfreq(len(y), 1 / 48e3)
    hyoty = Y[np.argmin(abs(f - 5e3))]
    alias = Y[np.argmin(abs(f - (40e3 - 48e3)))]   # 40 kHz -> -8 kHz
    suhde = 20 * np.log10(alias / hyoty)
    print(f"{nimi:15}: hairitsija kanavalla {suhde:6.1f} dB hyotysignaalista")
# @loppu tarkistus
