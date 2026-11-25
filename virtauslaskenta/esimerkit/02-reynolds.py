"""Reynoldsin ja Machin luku arkisille virtauksille: mitä tehtävästä
tiedetään ennen kuin mitään lasketaan."""

from dataclasses import dataclass

# @alku luvut
AANEN_NOPEUS = {"ilma": 340.0, "vesi": 1480.0, "muu": 1500.0}   # m/s


@dataclass(frozen=True)
class Virtaus:
    nimi: str
    aine: str
    nopeus: float       # tyypillinen nopeus U, m/s
    mitta: float        # tyypillinen mitta L, m
    nu: float           # kinemaattinen viskositeetti, m²/s

    @property
    def reynolds(self) -> float:
        return self.nopeus * self.mitta / self.nu

    @property
    def mach(self) -> float:
        return self.nopeus / AANEN_NOPEUS[self.aine]


def luonne(re: float) -> str:
    """Karkea jako; tarkka raja riippuu geometriasta."""
    if re < 1.0:
        return "viskositeetti hallitsee"
    if re < 2000.0:
        return "laminaari"
    return "yleensä turbulentti"
# @loppu luvut


# @alku taulukko
VIRTAUKSET = (
    Virtaus("bakteeri vedessä", "vesi", 30e-6, 2e-6, 1.0e-6),
    Virtaus("hunaja lusikasta", "muu", 0.05, 0.01, 7e-3),
    Virtaus("voitelukalvo laakerissa", "muu", 5.0, 50e-6, 3e-5),
    Virtaus("vesi hanasta", "vesi", 1.0, 0.012, 1.0e-6),
    Virtaus("tuuli talon ympärillä", "ilma", 8.0, 10.0, 1.5e-5),
    Virtaus("henkilöauto maantiellä", "ilma", 28.0, 4.5, 1.5e-5),
    Virtaus("matkustajakoneen siipi", "ilma", 230.0, 5.0, 3.5e-5),
)

print(f"{'virtaus':26s} {'Re':>8s} {'Ma':>7s}  luonne")
for v in VIRTAUKSET:
    kokoon = "" if v.mach < 0.3 else "  (kokoonpuristuva)"
    print(f"{v.nimi:26s} {v.reynolds:8.1e} {v.mach:7.1e}  "
          f"{luonne(v.reynolds)}{kokoon}")
# @loppu taulukko
