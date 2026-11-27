"""Tehomittarilohkon testi ilman GNU Radiota: palojen koko ei saa
vaikuttaa tulokseen."""

import numpy as np

from tehomittari import Kompleksi, Reaali, TehoMittari


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
