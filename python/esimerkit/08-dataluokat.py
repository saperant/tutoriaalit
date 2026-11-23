"""Dataluokat: arvo-oliot vähällä koodilla."""

from dataclasses import dataclass, field, replace
from datetime import date


# @alku tilaus
@dataclass(frozen=True, slots=True, order=True)
class Versio:
    paa: int
    sivu: int = 0
    korjaus: int = 0

    @classmethod
    def jasenna(cls, teksti: str) -> "Versio":
        osat = [int(o) for o in teksti.split(".")]
        return cls(*osat)

    def __str__(self) -> str:
        return f"{self.paa}.{self.sivu}.{self.korjaus}"


@dataclass(slots=True)
class Julkaisu:
    versio: Versio
    paiva: date
    muutokset: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.paiva.year < 2000:
            raise ValueError(f"epäuskottava päiväys: {self.paiva}")
# @loppu tilaus


# @alku kaytto
versiot = [Versio.jasenna(v) for v in ["1.10.0", "1.2.3", "1.9"]]
print([str(v) for v in sorted(versiot)])
print(Versio(1, 2) == Versio.jasenna("1.2.0"))
print({Versio(1, 0), Versio(1, 0, 0)})          # frozen: hajautettava

julkaisu = Julkaisu(Versio(2, 0), date(2026, 11, 1))
julkaisu.muutokset.append("uusi rajapinta")
korjaus = replace(julkaisu.versio, korjaus=1)   # uusi olio, vanha ennallaan
print(julkaisu.versio, julkaisu.paiva, julkaisu.muutokset)
print(korjaus)
try:
    Julkaisu(Versio(0, 1), date(1999, 1, 1))
except ValueError as virhe:
    print("hylätty:", virhe)
# @loppu kaytto
