"""CSMA/CD ja binäärinen eksponentiaalinen perääntyminen (BEB)."""

import numpy as np

rng = np.random.default_rng(8)


# @alku beb
def kilpailu(asemia: int) -> int:
    """Kaikilla asemilla on kehys lähetettävänä. Palauttaa, montako
    aikaviipaletta kului ennen kuin ensimmäinen kehys meni läpi."""
    tormayksia = np.zeros(asemia, dtype=np.int64)
    odotus = np.zeros(asemia, dtype=np.int64)
    viipaleita = 0
    while True:
        viipaleita += 1
        valmiit = np.flatnonzero(odotus == 0)
        if len(valmiit) == 1:
            return viipaleita
        if len(valmiit) > 1:                       # törmäys
            tormayksia[valmiit] += 1
            ylaraja = 2 ** np.minimum(tormayksia[valmiit], 10)
            odotus[valmiit] = rng.integers(0, ylaraja) + 1
        odotus[odotus > 0] -= 1
# @loppu beb


for asemia in (2, 5, 20, 50):
    tulokset = [kilpailu(asemia) for _ in range(2000)]
    print(f"{asemia:>3} asemaa: keskimäärin {np.mean(tulokset):5.2f}"
          f" viipaletta kilpailuun (suurin {max(tulokset)})")
