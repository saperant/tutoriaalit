"""Paineyhtälön ratkaisijat: Jacobi, liittogradientti ja monihila.

Poissonin yhtälö -lap(u) = f yksikköneliössä, reunoilla u = 0, viiden
pisteen kaavalla. Taulukoissa on mukana reunapisteiden kehys, joten
sisäpisteitä on n x n ja taulukon koko (n + 2) x (n + 2)."""

import numpy as np
import numpy.typing as npt

Taulukko = npt.NDArray[np.float64]
TAVOITE = 1e-8        # jäännöksen normi suhteessa alkuun


# @alku perus
def jaannos(u: Taulukko, f: Taulukko, h: float) -> Taulukko:
    """r = f - A u sisäpisteissä; kehys on nolla."""
    r = np.zeros_like(u)
    r[1:-1, 1:-1] = f[1:-1, 1:-1] - (
        4.0 * u[1:-1, 1:-1] - u[:-2, 1:-1] - u[2:, 1:-1]
        - u[1:-1, :-2] - u[1:-1, 2:]) / h**2
    return r


def jacobi(u: Taulukko, f: Taulukko, h: float, kertoja: float = 0.8
           ) -> Taulukko:
    """Yksi vaimennettu Jacobin kierros: korjaus on jäännös kertaa h²/4."""
    tulos: Taulukko = u + kertoja * h**2 / 4.0 * jaannos(u, f, h)
    return tulos
# @loppu perus


# @alku monihila
def karkeista(r: Taulukko) -> Taulukko:
    """Jäännös joka toiseen pisteeseen naapurien painotettuna keskiarvona."""
    m = (r.shape[0] - 1) // 2 + 1
    karkea = np.zeros((m, m))
    karkea[1:-1, 1:-1] = (
        4.0 * r[2:-2:2, 2:-2:2]
        + 2.0 * (r[1:-3:2, 2:-2:2] + r[3:-1:2, 2:-2:2]
                 + r[2:-2:2, 1:-3:2] + r[2:-2:2, 3:-1:2])
        + r[1:-3:2, 1:-3:2] + r[1:-3:2, 3:-1:2]
        + r[3:-1:2, 1:-3:2] + r[3:-1:2, 3:-1:2]) / 16.0
    return karkea


def hienonna(e: Taulukko) -> Taulukko:
    """Korjaus karkealta hilalta hienolle lineaarisella interpoloinnilla."""
    m = 2 * (e.shape[0] - 1) + 1
    hieno = np.zeros((m, m))
    hieno[::2, ::2] = e
    hieno[1::2, ::2] = 0.5 * (e[:-1, :] + e[1:, :])
    hieno[:, 1::2] = 0.5 * (hieno[:, :-1:2] + hieno[:, 2::2])
    return hieno


def v_kierros(u: Taulukko, f: Taulukko, h: float) -> Taulukko:
    """Tasoita, ratkaise jäännösyhtälö karkeammalla hilalla, tasoita."""
    if u.shape[0] == 3:                       # yksi sisäpiste: tarkka
        u = u.copy()
        u[1, 1] = h**2 * f[1, 1] / 4.0
        return u
    for _ in range(2):
        u = jacobi(u, f, h)
    karkea = karkeista(jaannos(u, f, h))
    u = u + hienonna(v_kierros(np.zeros_like(karkea), karkea, 2.0 * h))
    for _ in range(2):
        u = jacobi(u, f, h)
    return u
# @loppu monihila


# @alku liittogradientti
def liittogradientti(f: Taulukko, h: float) -> int:
    """Kierrosten määrä tavoitteeseen; A u lasketaan jäännösfunktiolla."""
    u = np.zeros_like(f)
    r = jaannos(u, f, h)
    p = r.copy()
    rr = float(np.sum(r * r))
    alku = rr
    kierroksia = 0
    while rr > TAVOITE**2 * alku:
        ap = -jaannos(p, np.zeros_like(f), h)
        alfa = rr / float(np.sum(p * ap))
        u += alfa * p
        r -= alfa * ap
        uusi = float(np.sum(r * r))
        p = r + uusi / rr * p
        rr = uusi
        kierroksia += 1
    return kierroksia
# @loppu liittogradientti


# @alku vertailu
def kierroksia(menetelma: str, f: Taulukko, h: float) -> int:
    def normi2(r: Taulukko) -> float:
        return float(np.sum(r * r))

    u = np.zeros_like(f)
    alku = normi2(jaannos(u, f, h))
    maara = 0
    while normi2(jaannos(u, f, h)) > TAVOITE**2 * alku:
        u = (jacobi(u, f, h, 1.0) if menetelma == "jacobi"
             else v_kierros(u, f, h))
        maara += 1
    return maara


print("sisäpisteitä/sivu  Jacobi  liittogradientti  monihila (V-kierroksia)")
for n in (15, 31, 63, 127):
    h = 1.0 / (n + 1)
    x: Taulukko = np.linspace(0.0, 1.0, n + 2)
    f: Taulukko = np.zeros((n + 2, n + 2))
    f[1:-1, 1:-1] = (np.exp(x[1:-1, None]) * np.sin(3.0 * x[None, 1:-1])
                     + np.where(x[1:-1, None] > 0.5, 5.0, 0.0))
    jac = f"{kierroksia('jacobi', f, h):6d}" if n <= 63 else "     –"
    print(f"{n:17d}  {jac} {liittogradientti(f, h):17d}"
          f" {kierroksia('monihila', f, h):9d}")
# @loppu vertailu
