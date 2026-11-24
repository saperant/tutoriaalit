"""Lohkoittainen suodatus ilman tilaa: vertailu referenssiin paljastaa."""

import numpy as np
from scipy import signal

# @alku virhe
b, a = [0.1], [1.0, -0.9]                    # EMA, alfa = 0.1
x = np.random.default_rng(1).normal(size=400)
odotettu = signal.lfilter(b, a, x)
# Virhe: jokainen 100 näytteen lohko alkaa nollatilasta.
lohkoittain = np.concatenate([signal.lfilter(b, a, x[i:i + 100])
                              for i in range(0, len(x), 100)])
np.testing.assert_allclose(lohkoittain, odotettu, rtol=0, atol=1e-9)
# @loppu virhe
