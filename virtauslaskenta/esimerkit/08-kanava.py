"""Kanavavirtauksen kehittyminen: tasainen sisäänvirtaus muuttuu
paraabeliksi. Tarkistukset: tilavuusvirta, profiili ja painegradientti."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "07-virta"))
from virta import (  # noqa: E402
    Ratkaisija,
    Reuna,
    Taulukko,
    Tehtava,
    Tila,
    tasapainoon,
    vakaa_askel,
)

# @alku tehtava
KORKEUS = 1.0
U_KESKI = 1.0
NY = 24


def kanava(reynolds: float, pituus: float) -> tuple[Tehtava, Tila, int]:
    """Vasemmalta tasainen nopeus, oikealla ulosvirtaus, ylä- ja alareuna
    seiniä. Reynoldsin luku on U H / nu."""
    teht = Tehtava(round(pituus * NY), NY, pituus, KORKEUS,
                   U_KESKI * KORKEUS / reynolds,
                   vasen=Reuna("sisään", U_KESKI), oikea=Reuna("ulos"))
    ratkaisija = Ratkaisija(teht)
    tila, askelia = tasapainoon(ratkaisija, ratkaisija.lepotila(),
                                vakaa_askel(teht, 1.6 * U_KESKI), raja=1e-7)
    return teht, tila, askelia


def keskilinja(tila: Tila) -> Taulukko:
    """Vaakanopeus kanavan puolivälissä jokaisella pystypinnalla."""
    tulos: Taulukko = 0.5 * (tila.u[:, NY // 2 - 1] + tila.u[:, NY // 2])
    return tulos
# @loppu tehtava


# @alku tarkistukset
teht, tila, askelia = kanava(40.0, 6.0)
print(f"Re = 40, hila {teht.nx} x {teht.ny}, tasapaino noin "
      f"{round(askelia, -2)} askeleessa")
virta = np.sum(tila.u, axis=1) * teht.dy
print(f"tilavuusvirta jokaisessa poikkileikkauksessa sama (ero alle 1e-10): "
      f"{bool(np.max(np.abs(virta - U_KESKI * KORKEUS)) < 1e-10)}")

uc = keskilinja(tila)
print("keskilinjan nopeus:  " + "  ".join(
    f"x={x:g}: {uc[round(x / teht.dx)]:.3f}"
    for x in (0.0, 0.5, 1.0, 2.0, 4.0)))

y: Taulukko = (np.arange(NY, dtype=np.float64) + 0.5) * teht.dy
paraabeli = 6.0 * U_KESKI * y * (KORKEUS - y) / KORKEUS**2
i = round(5.0 / teht.dx)
print(f"profiili kohdassa x = 5: suurin ero paraabeliin "
      f"{float(np.max(np.abs(tila.u[i, :] - paraabeli))):.4f}")
dpdx = float(tila.p[i + 6, NY // 2] - tila.p[i - 6, NY // 2]) / (12 * teht.dx)
print(f"painegradientti: laskettu {dpdx:.4f}, "
      f"teoria -12 nu U / H² = {-12.0 * teht.nu * U_KESKI / KORKEUS**2:.4f}")
# @loppu tarkistukset

# @alku kehittyminen
print("kehittymispituus: keskilinjan nopeus 99 % lopullisesta")
print("   Re  pituus L  L / (Re H)")
for reynolds, pituus in ((20.0, 6.0), (40.0, 6.0), (80.0, 10.0)):
    teht, tila, _ = kanava(reynolds, pituus)
    uc = keskilinja(tila)
    x: Taulukko = np.arange(teht.nx + 1, dtype=np.float64) * teht.dx
    kehittynyt = float(np.interp(0.99 * uc[-1], uc, x))
    print(f"{reynolds:5.0f} {kehittynyt:9.2f} {kehittynyt / reynolds:11.3f}")
# @loppu kehittyminen
