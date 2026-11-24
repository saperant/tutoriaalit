"""GNU Radion lohkon logiikka ilman GNU Radiota.

GNU Radion ajastin kutsuu lohkon work-metodia vaihtelevan kokoisilla
paloilla. Lohkon on sailytettava tilansa kutsujen valilla, jotta tulos
ei riipu palojen koosta. Tassa lohkon logiikka on tavallinen luokka,
jonka voi testata ilman GNU Radiota; varsinainen gr.decim_block-kaare
nayttaa samalta (luku 9).
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


# @alku ajastin
def aja(lohko: TehoMittari, signaali: Kompleksi,
        palakoot: list[int]) -> Reaali:
    """Jaljittelee ajastinta: tulo annetaan paloina, lahdon tila
    kasvatetaan sen mukaan, montako naytetta lohko tuotti."""
    tulokset: list[Reaali] = []
    alku, i = 0, 0
    while alku + lohko.desimointi <= len(signaali):
        koko = palakoot[i % len(palakoot)] * lohko.desimointi
        tulo = signaali[alku:alku + koko]
        lahto = np.empty(len(tulo) // lohko.desimointi, dtype=np.float32)
        tuotettu = lohko.work([tulo], [lahto])
        tulokset.append(lahto[:tuotettu])
        alku += tuotettu * lohko.desimointi
        i += 1
    return np.concatenate(tulokset)
# @loppu ajastin


# @alku testi
rng = np.random.default_rng(14)
taso = np.repeat([0.01, 0.1, 0.03], 4000)
signaali = (taso * (rng.standard_normal(len(taso))
                    + 1j * rng.standard_normal(len(taso)))).astype(
    np.complex64)
kerralla = aja(TehoMittari(100), signaali, [10_000])
paloina = aja(TehoMittari(100), signaali, [1, 7, 3, 50, 2])
print(f"lahtoja {len(kerralla)}, paloina sama: "
      f"{np.array_equal(kerralla, paloina)}")
for k in (35, 39, 75, 79, 115, 119):
    print(f"lahto {k:3}: {kerralla[k]:6.1f} dBFS")
# @loppu testi
