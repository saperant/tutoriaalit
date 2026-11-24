"""Kosketinvärähtelyn poisto: RC-suodin ja Schmitt-liipaisin."""

import numpy as np
import numpy.typing as npt

from spice import HAKEMISTO, simuloi

# @alku schmitt
def tilat(u: npt.NDArray[np.float64], ala: float, yla: float) -> list[int]:
    """Logiikkatulon tilat. Schmitt-liipaisin vaihtaa tilaa vasta, kun
    jännite ylittää ylärajan tai alittaa alarajan (hystereesi)."""
    tila = 1 if u[0] > yla else 0
    tulos = [tila]
    for arvo in u[1:]:
        if tila == 0 and arvo > yla:
            tila = 1
        elif tila == 1 and arvo < ala:
            tila = 0
        tulos.append(tila)
    return tulos


def muutokset(tilat: list[int]) -> int:
    return sum(a != b for a, b in zip(tilat, tilat[1:], strict=False))
# @loppu schmitt


# @alku vertailu
# Tavallinen tulo: yksi kynnys 1,65 V. Schmitt-tulo: 1,0 V ja 2,3 V.
piiri = (HAKEMISTO / "04-varahtely.cir").read_text("utf-8")
print("tilamuutoksia yhdestä painalluksesta:")
for C in ("22n", "100n"):
    teksti = piiri.replace("C1 suod 0 22n", f"C1 suod 0 {C}")
    data = simuloi(teksti).data["varahtely"]
    raaka, suod = data[:, 1], data[:, 3]   # wrdata: (t, u) pareittain
    if C == "22n":
        print(f"  {'raaka, yksi kynnys':<26}"
              f"{muutokset(tilat(raaka, 1.65, 1.65))}")
        print(f"  {'raaka, Schmitt':<26}{muutokset(tilat(raaka, 1.0, 2.3))}")
    print(f"  {'RC ' + C + ', yksi kynnys':<26}"
          f"{muutokset(tilat(suod, 1.65, 1.65))}")
    print(f"  {'RC ' + C + ', Schmitt':<26}"
          f"{muutokset(tilat(suod, 1.0, 2.3))}")
# @loppu vertailu
