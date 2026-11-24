"""Interpolointipolynomi Newtonin muodossa: jaetut erotukset."""


# @alku erotukset
def jaetut_erotukset(x: list[float], y: list[float]) -> list[float]:
    """Kertoimet c_k = f[x_0, ..., x_k] taulukosta paikan päällä."""
    c = list(y)
    n = len(x)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            c[i] = (c[i] - c[i - 1]) / (x[i] - x[i - j])
    return c


def arvo(c: list[float], x: list[float], t: float) -> float:
    """p(t) Hornerin tapaan: c0 + (t-x0)(c1 + (t-x1)(c2 + ...))."""
    tulos = c[-1]
    for k in range(len(c) - 2, -1, -1):
        tulos = tulos * (t - x[k]) + c[k]
    return tulos
# @loppu erotukset


# @alku esimerkki
# Lämpötila mitattu neljänä hetkenä; arvio hetkellä 2.5 h.
ajat = [0.0, 1.0, 2.0, 4.0]
lampo = [12.0, 15.0, 17.0, 16.0]
c = jaetut_erotukset(ajat, lampo)
print("kertoimet:", " ".join(f"{v:.4f}" for v in c))
print(f"p(2.5) = {arvo(c, ajat, 2.5):.4f}")
# Uusi mittaus hetkellä 3 h: vanhat kertoimet säilyvät, yksi lisätään.
c5 = jaetut_erotukset([*ajat, 3.0], [*lampo, 17.0])
print("uudet kertoimet:", " ".join(f"{v:.4f}" for v in c5))
print(f"p(2.5) = {arvo(c5, [*ajat, 3.0], 2.5):.4f}")
# @loppu esimerkki
