"""Puoliintumisaika mittauksista: logaritmi suoristaa eksponentin."""

import numpy as np

# @alku mittaukset
# Kondensaattorin jännite purkautumisen aikana (V), näyte 0.5 s välein.
# Mittauksissa on pientä kohinaa (kiinteä siemen).
rng = np.random.default_rng(7)
t = np.arange(0.0, 5.01, 0.5)
tau_tosi = 1.6                                    # aikavakio RC, s
u = 9.0 * np.exp(-t / tau_tosi) * (1 + 0.01 * rng.normal(size=t.size))
# @loppu mittaukset

# @alku sovitus
# ln u = ln U0 - t / tau on suora: sovitetaan ensimmäisen asteen polynomi.
kulma, vakio = np.polyfit(t, np.log(u), 1)
tau = -1 / kulma
print(f"U0 = {np.exp(vakio):.2f} V, tau = {tau:.3f} s "
      f"(todellinen {tau_tosi} s)")
print(f"puoliintumisaika tau * ln 2 = {tau * np.log(2):.3f} s")
print(f"jännite 5 tau jälkeen: {100 * np.exp(-5):.2f} % alkuarvosta")
# @loppu sovitus
