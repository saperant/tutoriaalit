"""Riskirekisteri lukuina: altistus, varaus ja torjunnan kannattavuus."""

import random
from dataclasses import dataclass


# @alku rekisteri
@dataclass(frozen=True)
class Riski:
    nimi: str
    todennakoisyys: float
    vaikutus: tuple[float, float, float]   # paras, todennäköisin, huonoin pv
    torjunta: float = 0.0                  # torjunnan hinta päivinä
    # Torjunnan jälkeen: (todennäköisyys, vaikutuksen kerroin).
    torjuttuna: tuple[float, float] | None = None

    @property
    def keskivaikutus(self) -> float:
        return sum(self.vaikutus) / 3      # kolmiojakauman odotusarvo

    @property
    def altistus(self) -> float:
        return self.todennakoisyys * self.keskivaikutus

    @property
    def hyotysuhde(self) -> float:
        """Altistuksen lasku jaettuna torjunnan hinnalla."""
        if self.torjuttuna is None:
            return 0.0
        p, kerroin = self.torjuttuna
        return (self.altistus - p * kerroin * self.keskivaikutus) \
            / self.torjunta


REKISTERI = [
    Riski("maksurajapinnan toimittaja myöhästyy", 0.40, (5, 15, 40),
          torjunta=3, torjuttuna=(0.15, 1.0)),
    Riski("avainhenkilö lähtee kesken projektin", 0.15, (10, 20, 45),
          torjunta=6, torjuttuna=(0.15, 0.4)),
    Riski("suorituskyky ei riitä tuotantodatalla", 0.25, (5, 10, 30),
          torjunta=2, torjuttuna=(0.05, 1.0)),
    Riski("tietosuojavaatimus tulkittu väärin", 0.10, (10, 25, 60)),
    Riski("vanhan järjestelmän data on likaista", 0.60, (3, 8, 20),
          torjunta=2, torjuttuna=(0.30, 1.0)),
]
# @loppu rekisteri

print(f"{'riski':<40}{'p':>5}{'vaikutus':>9}{'altistus':>9}")
for r in sorted(REKISTERI, key=lambda r: -r.altistus):
    print(f"{r.nimi:<40}{r.todennakoisyys:>5.0%}"
          f"{r.keskivaikutus:>7.0f} pv{r.altistus:>6.1f} pv")
print(f"altistusten summa {sum(r.altistus for r in REKISTERI):.1f} pv")


# @alku simulointi
def toteuma(rng: random.Random, raja: float) -> float:
    """Yksi mahdollinen projekti. Torjutaan riskit, joiden hyötysuhde
    ylittää rajan."""
    paivat = 0.0
    for r in REKISTERI:
        p, kerroin = r.todennakoisyys, 1.0
        if r.torjuttuna is not None and r.hyotysuhde > raja:
            p, kerroin = r.torjuttuna
            paivat += r.torjunta
        if rng.random() < p:
            paras, todennakoisin, huonoin = r.vaikutus
            paivat += kerroin * rng.triangular(paras, huonoin, todennakoisin)
    return paivat


def jakauma(raja: float) -> list[float]:
    rng = random.Random(13)
    return sorted(toteuma(rng, raja) for _ in range(20_000))
# @loppu simulointi


print("torjunnan hyötysuhde (altistuksen lasku / hinta):")
for r in REKISTERI:
    if r.torjuttuna is not None:
        print(f"  {r.nimi:<40}{r.hyotysuhde:4.1f}")

print(f"{'torjutaan':<22}{'keskiarvo':>10}{'50 %':>8}{'85 %':>8}{'95 %':>8}")
for nimi, raja in (("ei mitään", 99.0), ("hyötysuhde yli 1", 1.0),
                   ("kaikki", -1.0)):
    j = jakauma(raja)
    print(f"{nimi:<22}{sum(j) / len(j):>7.1f} pv{j[len(j) // 2]:>5.0f} pv"
          f"{j[int(0.85 * len(j))]:>5.0f} pv{j[int(0.95 * len(j))]:>5.0f} pv")
