"""Lineaarisen tasojärjestelmän tasapainopisteen luokittelu."""

import numpy as np


# @alku luokittelu
def luokittele(A: np.ndarray) -> str:
    """Luokittelee origon tyypin jäljen ja determinantin avulla."""
    jalki = float(np.trace(A))
    det = float(np.linalg.det(A))
    diskr = jalki**2 - 4 * det
    if det < 0:
        return "satulapiste (epästabiili)"
    if abs(jalki) < 1e-12:
        return "keskus (ei vaimene)"
    suunta = "stabiili" if jalki < 0 else "epästabiili"
    if diskr < 0:
        return f"spiraali ({suunta})"
    return f"solmu ({suunta})"


ESIMERKIT = {
    "ylivaimennettu": [[0, 1], [-4, -5]],
    "alivaimennettu": [[0, 1], [-4, -1]],
    "vaimentamaton": [[0, 1], [-4, 0]],
    "satula": [[1, 0], [0, -2]],
    "kasvava spiraali": [[0.2, 1], [-1, 0.2]],
}
for nimi, matriisi in ESIMERKIT.items():
    A = np.array(matriisi, dtype=float)
    arvot = np.linalg.eigvals(A)
    # round(...) + 0.0 muuttaa mahdollisen miinusnollan nollaksi.
    teksti = ", ".join(
        f"{round(z.real, 2) + 0.0:+.2f}{round(z.imag, 2) + 0.0:+.2f}j"
        for z in sorted(arvot, key=lambda z: (z.real, z.imag))
    )
    print(f"{nimi:17s} {luokittele(A):26s} {teksti}")
# @loppu luokittelu
