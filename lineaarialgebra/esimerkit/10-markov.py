"""Potenssimenetelmä: Markovin ketjun tasapainojakauma."""

import numpy as np
import numpy.typing as npt

Vektori = npt.NDArray[np.float64]
Matriisi = npt.NDArray[np.float64]


# @alku potenssi
def potenssimenetelma(a: Matriisi, toleranssi: float = 1e-12,
                      kierroksia: int = 1000) -> tuple[float, Vektori, int]:
    """Itseisarvoltaan suurin ominaisarvo ja sen ominaisvektori.
    Toistuva kertolasku vahvistaa suurimman ominaisarvon suuntaa."""
    v = np.ones(a.shape[0]) / a.shape[0]
    arvo = 0.0
    for kierros in range(1, kierroksia + 1):
        w = a @ v
        uusi = float(np.linalg.norm(w, 1))
        w /= uusi
        if np.linalg.norm(w - v, 1) < toleranssi:
            return uusi, w, kierros
        v, arvo = w, uusi
    return arvo, v, kierroksia
# @loppu potenssi


# @alku ketju
# Kävijä siirtyy sivulta toiselle. Sarake j kertoo, minne sivulta j
# siirrytään; jokaisen sarakkeen summa on 1.
sivut = ["etusivu", "tuotteet", "ohjeet", "kassa"]
P = np.array([[0.1, 0.3, 0.5, 0.6],
              [0.6, 0.3, 0.2, 0.2],
              [0.2, 0.2, 0.2, 0.1],
              [0.1, 0.2, 0.1, 0.1]])
arvo, jakauma, kierroksia = potenssimenetelma(P)
print(f"suurin ominaisarvo {arvo:.6f} ({kierroksia} kierrosta)")
for nimi, osuus in zip(sivut, jakauma, strict=True):
    print(f"  {nimi:<8} {osuus:6.1%}")
# @loppu ketju

# @alku vertailu
arvot, vektorit = np.linalg.eig(P)
i = int(np.argmax(np.abs(arvot)))
v = np.real(vektorit[:, i])
print("np.linalg.eig sama:", bool(np.allclose(v / v.sum(), jakauma)))
toinen = sorted(np.abs(arvot))[-2]
print(f"|λ2| = {toinen:.3f}: virhe pienenee kertoimella {toinen:.3f}"
      " kierrosta kohti")
# @loppu vertailu
