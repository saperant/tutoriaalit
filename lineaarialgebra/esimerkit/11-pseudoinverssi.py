"""Pseudoinverssi ja pienin neliösumma singulaariarvohajotelmalla."""

import numpy as np
import numpy.typing as npt

Matriisi = npt.NDArray[np.float64]


# @alku pinv
def pseudoinverssi(a: Matriisi, rcond: float = 1e-12) -> Matriisi:
    """A+ = V S+ U^T: nollasta poikkeavat singulaariarvot käännetään,
    nollat (alle rcond * s_max) jätetään nolliksi."""
    u, s, vt = np.linalg.svd(a, full_matrices=False)
    kaannetyt = np.zeros_like(s)
    isot = s > rcond * s[0]
    kaannetyt[isot] = 1.0 / s[isot]
    return (vt.T * kaannetyt) @ u.T
# @loppu pinv


# @alku sovitus
# Luvun "Pienimmän neliösumman sovitus" kalibrointidata.
lampo = np.array([0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0])
jannite = np.array([0.502, 0.597, 0.708, 0.795, 0.903, 1.004, 1.091])
A = np.column_stack([np.ones_like(lampo), lampo])
a, b = pseudoinverssi(A) @ jannite
print(f"täysiasteinen: u = {a:.4f} V + {b * 1000:.3f} mV/°C · T")
print("sama kuin np.linalg.pinv:",
      bool(np.allclose(pseudoinverssi(A), np.linalg.pinv(A))))
# @loppu sovitus

# @alku vajaa
# Malliin lisätään sama lämpötila fahrenheiteina: F = 32 + 1,8 T on
# kahden muun sarakkeen lineaarikombinaatio, joten aste on 2 eikä 3.
A3 = np.column_stack([A, 32.0 + 1.8 * lampo])
s = np.linalg.svd(A3, compute_uv=False)
print("singulaariarvot:", [f"{x:.3g}" if x > 1e-9 else "~0" for x in s],
      "-> aste", int(np.linalg.matrix_rank(A3)))
print("normaaliyhtälöiden ehtoluku yli 1e15:",
      bool(np.linalg.cond(A3.T @ A3) > 1e15))
x = pseudoinverssi(A3) @ jannite
x_lstsq, *_ = np.linalg.lstsq(A3, jannite, rcond=None)
print("pseudoinverssi = lstsq:", bool(np.allclose(x, x_lstsq)))
print("ennusteet samat kuin kahden sarakkeen mallilla:",
      bool(np.allclose(A3 @ x, A @ np.array([a, b]))))
# Vajaa-asteisessa tehtävässä ratkaisuja on äärettömästi. Mikä tahansa
# nolla-avaruuden vektori voidaan lisätä; pseudoinverssi valitsee
# ratkaisuista lyhimmän.
nolla = np.array([32.0, 1.8, -1.0])            # A3 @ nolla = 0
toinen = x + 0.01 * nolla
print("toinen ratkaisu, sama jäännös:",
      bool(np.allclose(A3 @ toinen, A3 @ x)))
print("pseudoinverssin ratkaisu on lyhin:",
      bool(np.linalg.norm(x) < np.linalg.norm(toinen)))
print("ja kohtisuorassa nolla-avaruutta vastaan:",
      bool(np.isclose(x @ nolla, 0.0)))
# @loppu vajaa
