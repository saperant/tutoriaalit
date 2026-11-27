"""Tehomittarilohkon logiikka ilman GNU Radiota.

GNU Radion ajastin kutsuu lohkon work-metodia vaihtelevan kokoisilla
paloilla. Lohkon on sailytettava tilansa kutsujen valilla, jotta tulos
ei riipu palojen koosta. Logiikka on tavallinen luokka: main.py testaa
sen ilman GNU Radiota, ja gnuradio/lohkokaavio/tehomittari_gr.py kaarii
saman luokan GNU Radion lohkoksi.
"""

import numpy as np
from numpy.typing import NDArray

Kompleksi = NDArray[np.complex64]
Reaali = NDArray[np.float32]


# @alku lohko
class TehoMittari:
    """Desimoiva lohko: yksi tehoarvo (dBFS) jokaista N tulonaytetta
    kohti, eksponentiaalinen keskiarvo yli lahtojen."""

    def __init__(self, desimointi: int, alfa: float = 0.1) -> None:
        self.desimointi = desimointi
        self.alfa = alfa
        self.taso = 0.0                     # tila sailyy kutsujen valilla

    def work(self, input_items: list[Kompleksi],
             output_items: list[Reaali]) -> int:
        """GNU Radion sopimus decim_blockille: tuloa on N kertaa lahto,
        paluuarvo on tuotettujen lahtonaytteiden maara."""
        tulo, lahto = input_items[0], output_items[0]
        palat = tulo[:len(lahto) * self.desimointi].reshape(
            -1, self.desimointi)
        for i, pala in enumerate(palat):
            teho = float(np.mean(np.abs(pala) ** 2))
            self.taso += self.alfa * (teho - self.taso)
            lahto[i] = 10 * np.log10(self.taso + 1e-20)
        return len(palat)
# @loppu lohko
