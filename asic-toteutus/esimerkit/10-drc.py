"""Suunnittelusääntöjen tarkistus (DRC) ja antennisääntö.

Piirikuvio on suorakulmioita kerroksilla. Valmistaja antaa säännöt:
vähimmäisleveys, vähimmäisetäisyys ja läpiviennin reunus. Antenni-
sääntö rajoittaa metallin pinta-alaa, joka on kytketty transistorin
hilaan ennen kuin ylempi kerros yhdistää sen diffuusioon: valmistuksen
aikana kerääntyvä varaus voi muuten rikkoa hilaoksidin.
"""

from dataclasses import dataclass
from itertools import combinations


# @alku kuvio
@dataclass(frozen=True)
class Laatikko:
    nimi: str
    kerros: str
    x0: float
    y0: float
    x1: float
    y1: float                    # µm

    @property
    def leveys(self) -> float:
        return min(self.x1 - self.x0, self.y1 - self.y0)


SAANNOT = {"met1.leveys": 0.14, "met1.vali": 0.14, "via1.reunus": 0.05}

KUVIO = [
    Laatikko("johdin A", "met1", 0.0, 0.0, 2.0, 0.14),
    Laatikko("johdin B", "met1", 0.0, 0.26, 2.0, 0.40),   # väli 0.12
    Laatikko("johdin C", "met1", 3.0, 0.0, 3.10, 1.0),    # leveys 0.10
    Laatikko("johdin D", "met1", 2.4, 0.5, 2.8, 0.9),
    Laatikko("via E", "via1", 2.42, 0.6, 2.62, 0.8),      # reunus 0.02
]
# @loppu kuvio


# @alku tarkistus
def vali(a: Laatikko, b: Laatikko) -> float:
    dx = max(0.0, max(a.x0, b.x0) - min(a.x1, b.x1))
    dy = max(0.0, max(a.y0, b.y0) - min(a.y1, b.y1))
    return max(dx, dy) if min(dx, dy) == 0 else (dx**2 + dy**2) ** 0.5


def drc(kuvio: list[Laatikko]) -> list[str]:
    virheet = []
    met1 = [k for k in kuvio if k.kerros == "met1"]
    for k in met1:
        if k.leveys < SAANNOT["met1.leveys"] - 1e-9:
            virheet.append(f"{k.nimi}: leveys {k.leveys:.2f} µm")
    for a, b in combinations(met1, 2):
        v = vali(a, b)
        if 0 < v < SAANNOT["met1.vali"] - 1e-9:
            virheet.append(f"{a.nimi} – {b.nimi}: väli {v:.2f} µm")
    for via in (k for k in kuvio if k.kerros == "via1"):
        for m in met1:
            if vali(via, m) == 0:
                reunus = min(via.x0 - m.x0, m.x1 - via.x1,
                             via.y0 - m.y0, m.y1 - via.y1)
                if reunus < SAANNOT["via1.reunus"] - 1e-9:
                    virheet.append(f"{via.nimi} {m.nimi}:ssa: reunus "
                                   f"{reunus:.2f} µm")
    return virheet
# @loppu tarkistus


# @alku antenni
def antennisuhde(metallia_um2: float, hilaa_um2: float) -> float:
    return metallia_um2 / hilaa_um2
# @loppu antenni


def main() -> None:
    # @alku ajo
    print("DRC-rikkeet:")
    for v in drc(KUVIO):
        print("  " + v)
    hila = 0.15 * 0.5                       # yhden tulon hila-ala µm²
    for nimi, pituus in [("lyhyt johdin", 50), ("pitkä johdin", 400)]:
        suhde = antennisuhde(pituus * 0.14, hila)
        tila = "OK" if suhde <= 400 else "rike: lisää diodi tai hyppy"
        print(f"{nimi} {pituus} µm: antennisuhde {suhde:.0f} ({tila})")
    # @loppu ajo


if __name__ == "__main__":
    main()
