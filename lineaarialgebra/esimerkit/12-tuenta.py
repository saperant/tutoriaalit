"""Miksi eliminoinnissa tarvitaan osittaistuentaa."""

Matriisi = list[list[float]]
Vektori = list[float]


# @alku ilman
def ratkaise(a: Matriisi, b: Vektori, tuenta: bool) -> Vektori:
    n = len(a)
    m = [rivi[:] + [bi] for rivi, bi in zip(a, b, strict=True)]
    for k in range(n):
        if tuenta:
            p = max(range(k, n), key=lambda i: abs(m[i][k]))
            m[k], m[p] = m[p], m[k]
        for i in range(k + 1, n):
            kerroin = m[i][k] / m[k][k]
            for j in range(k, n + 1):
                m[i][j] -= kerroin * m[k][j]
    x = [0.0] * n
    for i in reversed(range(n)):
        s = sum(m[i][j] * x[j] for j in range(i + 1, n))
        x[i] = (m[i][n] - s) / m[i][i]
    return x
# @loppu ilman


# @alku vertailu
# Ratkaisu on käytännössä x = (1, 1). Pieni tukialkio 1e-17 tekee
# kertoimesta valtavan, ja ykkösen tieto häviää pyöristyksessä.
A = [[1e-17, 1.0], [1.0, 1.0]]
b = [1.0, 2.0]
print("ilman tuentaa:", ratkaise(A, b, tuenta=False))
print("tuennalla:    ", ratkaise(A, b, tuenta=True))
# @loppu vertailu
