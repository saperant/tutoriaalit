"""Gram–Schmidt: klassinen ja modifioitu, sekä QR-hajotelma."""

import numpy as np
import numpy.typing as npt

Matriisi = npt.NDArray[np.float64]


# @alku gs
def gram_schmidt(a: Matriisi, modifioitu: bool) -> Matriisi:
    """Sarakkeiden ortonormaali kanta Q. Klassinen versio vähentää
    alkuperäisen sarakkeen projektiot, modifioitu jo päivitetyn."""
    q = np.zeros_like(a)
    for j in range(a.shape[1]):
        v = a[:, j].copy()
        for i in range(j):
            lahde = v if modifioitu else a[:, j]
            v -= (q[:, i] @ lahde) * q[:, i]
        q[:, j] = v / np.linalg.norm(v)
    return q
# @loppu gs


# @alku vertailu
def ortogonaalisuusvirhe(q: Matriisi) -> float:
    """‖Q^T Q − I‖: nolla, jos sarakkeet ovat täsmälleen ortonormaaleja."""
    return float(np.linalg.norm(q.T @ q - np.eye(q.shape[1])))


# Lähes samansuuntaiset sarakkeet (Läuchlin matriisi).
e = 1e-8
A = np.array([[1.0, 1.0, 1.0], [e, 0, 0], [0, e, 0], [0, 0, e]])
for modifioitu in (False, True):
    virhe = ortogonaalisuusvirhe(gram_schmidt(A, modifioitu))
    nimi = "modifioitu" if modifioitu else "klassinen"
    arvio = "alle 1e-6" if virhe < 1e-6 else "yli 0.1" if virhe > 0.1 \
        else "välissä"
    print(f"{nimi:<10} ‖Q^T Q − I‖ {arvio}")
# @loppu vertailu

# @alku qr
# QR-hajotelma: A = QR, missä Q:n sarakkeet ovat ortonormaaleja ja R on
# yläkolmiomatriisi. NumPyn versio käyttää Householderin peilauksia.
M = np.array([[3.0, 1.0], [4.0, 2.0], [0.0, 2.0]])
Q, R = np.linalg.qr(M)
print("R on yläkolmio:", bool(np.allclose(R, np.triu(R))))
print("QR = A:", bool(np.allclose(Q @ R, M)))
print("Q^T Q = I:", bool(np.allclose(Q.T @ Q, np.eye(2))))
print("|R| =", (np.round(np.abs(R), 3) + 0.0).tolist())
# @loppu qr
