"""Kolmiulotteinen kamera: näkymämatriisi ja perspektiiviprojektio."""

import numpy as np
import numpy.typing as npt

Vektori = npt.NDArray[np.float64]
Matriisi = npt.NDArray[np.float64]


# @alku katse
def katse(silma: Vektori, kohde: Vektori, ylos: Vektori) -> Matriisi:
    """Näkymämatriisi (look-at): maailman koordinaatit kameran
    koordinaateiksi. Kamera katsoo negatiivisen z-akselin suuntaan."""
    f = (kohde - silma) / np.linalg.norm(kohde - silma)   # eteenpäin
    s = np.cross(f, ylos)
    s /= np.linalg.norm(s)                                 # oikealle
    u = np.cross(s, f)                                     # ylös
    m = np.eye(4)
    m[0, :3], m[1, :3], m[2, :3] = s, u, -f
    m[:3, 3] = -m[:3, :3] @ silma          # kierto ja sitten siirto
    return m
# @loppu katse


# @alku perspektiivi
def perspektiivi(fov_asteet: float, suhde: float, lahi: float,
                 kauka: float) -> Matriisi:
    """OpenGL-tyylinen projektio: näkökartio kuutioksi [-1, 1]³."""
    f = 1.0 / np.tan(np.radians(fov_asteet) / 2)
    return np.array([
        [f / suhde, 0.0, 0.0, 0.0],
        [0.0, f, 0.0, 0.0],
        [0.0, 0.0, (kauka + lahi) / (lahi - kauka),
         2 * kauka * lahi / (lahi - kauka)],
        [0.0, 0.0, -1.0, 0.0]])
# @loppu perspektiivi


# @alku projisointi
nakyma = katse(np.array([0.0, 2.0, 5.0]), np.array([0.0, 0.0, 0.0]),
               np.array([0.0, 1.0, 0.0]))
projektio = perspektiivi(60.0, 16 / 9, 0.1, 100.0)
for nimi, p in [("origo", [0.0, 0.0, 0.0]), ("lähellä", [1.0, 0.0, 3.0]),
                ("kaukana", [1.0, 0.0, -20.0])]:
    leike = projektio @ nakyma @ np.array([*p, 1.0])
    ndc = leike[:3] / leike[3]              # perspektiivijako w:llä
    print(f"{nimi:<8} w = {leike[3]:6.2f}  x = {round(ndc[0], 3) + 0.0:6.3f}"
          f"  syvyys = {ndc[2]:.4f}")
# @loppu projisointi
