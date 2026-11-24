"""Gaussin eliminointi ilman tuentaa ja osittaisella tuennalla."""


# @alku gauss
def ratkaise(A: list[list[float]], b: list[float],
             tuenta: bool) -> list[float]:
    """Ratkaisee Ax = b. Tuennalla rivejä vaihdetaan niin, että
    jakajana on sarakkeen itseisarvoltaan suurin alkio."""
    n = len(b)
    A = [rivi[:] + [bi] for rivi, bi in zip(A, b, strict=True)]
    for k in range(n):
        if tuenta:
            p = max(range(k, n), key=lambda i: abs(A[i][k]))
            A[k], A[p] = A[p], A[k]
        for i in range(k + 1, n):
            kerroin = A[i][k] / A[k][k]        # pieni jakaja: suuri kerroin
            for j in range(k, n + 1):
                A[i][j] -= kerroin * A[k][j]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = sum(A[i][j] * x[j] for j in range(i + 1, n))
        x[i] = (A[i][n] - s) / A[i][i]
    return x
# @loppu gauss


# @alku kokeilu
# Tarkka ratkaisu on hyvin lähellä (1, 1), ja matriisi on hyvin ehdollinen
# (ehtoluku noin 2.6). Ongelma on algoritmissa, ei tehtävässä.
A = [[1e-20, 1.0], [1.0, 1.0]]
b = [1.0, 2.0]
print("ilman tuentaa: ", ratkaise(A, b, tuenta=False))
print("tuennalla:     ", ratkaise(A, b, tuenta=True))
# @loppu kokeilu
