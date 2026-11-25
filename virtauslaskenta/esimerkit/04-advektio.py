"""Advektioyhtälö c_t + u c_x = 0 neljällä kaaviolla.

Jaksollinen alue, nopeus 1: yhden kierroksen jälkeen tarkka ratkaisu on
sama kuin alkutila. Kaikki kaaviot ovat säilyvässä muodossa: uusi arvo
on vanha miinus pintojen voiden erotus."""

import math
from collections.abc import Callable

import numpy as np
import numpy.typing as npt

Taulukko = npt.NDArray[np.float64]
Vuo = Callable[[Taulukko, float], Taulukko]


# @alku vuot
def keskeis(c: Taulukko, courant: float) -> Taulukko:
    """Oikean pinnan arvo naapurien keskiarvona."""
    tulos: Taulukko = 0.5 * (c + np.roll(c, -1))
    return tulos


def vastavirta(c: Taulukko, courant: float) -> Taulukko:
    """Pinnan arvo tulosuunnan ruudusta (u > 0: vasemmalta)."""
    return c


def lax_wendroff(c: Taulukko, courant: float) -> Taulukko:
    """Vastavirta-arvo ja korjaus, joka tekee kaaviosta toista kertalukua
    ajassa ja paikassa."""
    tulos: Taulukko = c + 0.5 * (1.0 - courant) * (np.roll(c, -1) - c)
    return tulos


def rajoitettu(c: Taulukko, courant: float) -> Taulukko:
    """Lax–Wendroffin korjaus kerrottuna rajoittimella (van Leer).

    r vertaa peräkkäisiä erotuksia: sileässä kohdassa r on lähellä yhtä
    ja korjaus on täysi, ääriarvossa r < 0 ja korjaus on nolla."""
    eteen = np.roll(c, -1) - c
    taakse = c - np.roll(c, 1)
    turvallinen = np.where(eteen == 0.0, 1.0, eteen)
    r = np.where(eteen == 0.0, 0.0, taakse / turvallinen)
    psi = (r + np.abs(r)) / (1.0 + np.abs(r))
    tulos: Taulukko = c + 0.5 * psi * (1.0 - courant) * eteen
    return tulos


def askel(c: Taulukko, courant: float, vuo: Vuo) -> Taulukko:
    """c_uusi = c - C (c_oikea_pinta - c_vasen_pinta)."""
    pinta = vuo(c, courant)
    uusi: Taulukko = c - courant * (pinta - np.roll(pinta, 1))
    return uusi
# @loppu vuot


KAAVIOT: tuple[tuple[str, Vuo], ...] = (
    ("keskeis", keskeis), ("vastavirta", vastavirta),
    ("Lax–Wendroff", lax_wendroff), ("rajoitettu", rajoitettu))


# @alku kierros
def kierros(alku: Taulukko, courant: float, vuo: Vuo) -> Taulukko:
    """Yksi kierros jaksollisen alueen ympäri."""
    c = alku.copy()
    for _ in range(round(len(alku) / courant)):
        c = askel(c, courant, vuo)
    return c


def porras_ja_kumpu(n: int) -> Taulukko:
    x: Taulukko = (np.arange(n, dtype=np.float64) + 0.5) / n
    kumpu = np.exp(-(((x - 0.25) / 0.05) ** 2))
    porras = np.where((x > 0.6) & (x < 0.8), 1.0, 0.0)
    tulos: Taulukko = kumpu + porras
    return tulos
# @loppu kierros


# @alku vertailu
if __name__ == "__main__":
    alku = porras_ja_kumpu(100)
    print("kaavio         määrä   pienin  suurin  keskivirhe")
    for nimi, vuo in KAAVIOT:
        c = kierros(alku, 0.5, vuo)
        if float(np.max(np.abs(c))) > 100.0:
            print(f"{nimi:13s} ratkaisu kasvaa rajatta")
            continue
        pienin = round(float(np.min(c)), 3) + 0.0
        print(f"{nimi:13s} {float(np.sum(c) / np.sum(alku)):6.4f}"
              f" {pienin:7.3f} {float(np.max(c)):7.3f}"
              f" {float(np.mean(np.abs(c - alku))):11.4f}")
# @loppu vertailu

# @alku kertaluku
    print()
    print("sileä alkutila sin(2 pi x): keskivirhe ja kertaluku")
    print("ruutuja  vastavirta       Lax–Wendroff     rajoitettu")
    edelliset = [0.0, 0.0, 0.0]
    for n in (50, 100, 200, 400):
        x: Taulukko = (np.arange(n, dtype=np.float64) + 0.5) / n
        sini: Taulukko = np.sin(2.0 * math.pi * x)
        rivi = f"{n:7d}"
        for k, (_, vuo) in enumerate(KAAVIOT[1:]):
            virhe = float(np.mean(np.abs(kierros(sini, 0.5, vuo) - sini)))
            p = (f"{math.log2(edelliset[k] / virhe):5.2f}"
                 if edelliset[k] else "    -")
            rivi += f"  {virhe:8.1e} {p}"
            edelliset[k] = virhe
        print(rivi)
# @loppu kertaluku
