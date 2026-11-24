"""Pakettivirhesuhde: simuloitu linkki ihanteellista tahdistusta vastaan."""

import numpy as np
from linkki import Kanava, laheta, vastaanota
from scipy.special import erfc

# @alku per
rng = np.random.default_rng(18)
tavuja, paketteja = 32, 1_000
bitteja = 8 * (tavuja + 2)
print("Eb/N0   PER: ilman seurantaa   seurannalla   ihanteellinen")
for EbN0_dB in (4.0, 6.0, 8.0, 10.0):
    vaarin = np.zeros(2, dtype=int)
    for _ in range(paketteja):
        data = rng.integers(0, 256, tavuja, dtype=np.uint8).tobytes()
        kanava = Kanava(viive=int(rng.integers(0, 40)),
                        taajuus=float(rng.uniform(-2e-3, 2e-3)),
                        vaihe=float(rng.uniform(0, 2 * np.pi)),
                        EbN0_dB=EbN0_dB)
        r = kanava.lapi(laheta(data), rng)
        for i, seuranta in enumerate((False, True)):
            vaarin[i] += vastaanota(r, tavuja, seuranta) != data
    ber = 0.5 * erfc(np.sqrt(10 ** (EbN0_dB / 10)))
    ihanne = 1 - (1 - ber) ** bitteja         # tunnettu ajoitus ja vaihe
    ilman, seurannalla = vaarin / paketteja
    print(f"{EbN0_dB:4.0f} dB   {ilman:20.3f}   {seurannalla:11.3f}"
          f"   {ihanne:13.3f}")
# @loppu per
