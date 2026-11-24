"""Kellopuu: sama kello 16 kiikulle, vinous ja johdinpituus.

Kello jaetaan kiikuille ketjuna lähimmästä kiikusta seuraavaan sekä
H-puuna, jossa jokaisen kiikun polku juuresta on yhtä pitkä, ilman
puskureita ja puskureilla haarautumiskohdissa. Viive lasketaan
Elmore-mallilla: jokaisen johdinpalan vastus kertaa sen alapuolella
oleva kapasitanssi.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# @alku parametrit
R_JOHDIN = 0.08      # Ω/µm
C_JOHDIN = 0.20e-15  # F/µm
C_KIIKKU = 2.5e-15   # F, kiikun kellotulo
R_AJURI = 1000.0     # Ω, kellopuskurin lähtöresistanssi
C_PUSKURI = 4.5e-15  # F, puskurin tulo
T_PUSKURI = 60e-12   # s, puskurin sisäinen viive
# @loppu parametrit


# @alku elmore
@dataclass
class Solmu:
    x: float
    y: float
    lapset: list[Solmu] = field(default_factory=list)
    kiikku: bool = False
    puskuri: bool = False

    def alavirta(self) -> float:
        """Kaikki solmun alapuolinen kapasitanssi."""
        oma = C_KIIKKU if self.kiikku else 0.0
        return oma + sum(C_JOHDIN * etaisyys(self, k) + k.kapasitanssi()
                         for k in self.lapset)

    def kapasitanssi(self) -> float:
        """Ylävirtaan näkyvä kuorma: puskuri erottaa alavirran."""
        return C_PUSKURI if self.puskuri else self.alavirta()


def etaisyys(a: Solmu, b: Solmu) -> float:
    return abs(a.x - b.x) + abs(a.y - b.y)       # reititys suorakulmin


def viiveet(juuri: Solmu) -> list[float]:
    """Elmore-viive jokaiselle kiikulle (s)."""
    tulos: list[float] = []

    def kulje(s: Solmu, viive: float) -> None:
        if s.puskuri:
            viive += T_PUSKURI + R_AJURI * s.alavirta()
        if s.kiikku:
            tulos.append(viive)
        for k in s.lapset:
            r = R_JOHDIN * etaisyys(s, k)
            c = C_JOHDIN * etaisyys(s, k) / 2 + k.kapasitanssi()
            kulje(k, viive + r * c)

    kulje(juuri, R_AJURI * juuri.alavirta())
    return tulos


def pituus(s: Solmu) -> float:
    return sum(etaisyys(s, k) + pituus(k) for k in s.lapset)
# @loppu elmore


# @alku rakenteet
KIIKUT = [(125.0 + 250 * i, 125.0 + 250 * j)
          for j in range(4) for i in range(4)]       # 1 mm × 1 mm


def ketju() -> Solmu:
    """Juuri vasemmassa alakulmassa, kiikut käärmejärjestyksessä."""
    juuri = Solmu(0.0, 0.0)
    edellinen = juuri
    for j in range(4):
        rivi = KIIKUT[4 * j:4 * j + 4]
        for x, y in (rivi if j % 2 == 0 else rivi[::-1]):
            s = Solmu(x, y, kiikku=True)
            edellinen.lapset.append(s)
            edellinen = s
    return juuri


def h_puu(x: float, y: float, koko: float, taso: int,
          puskurit: bool = False) -> Solmu:
    """H-puu: keskeltä neljään neljännekseen rekursiivisesti."""
    s = Solmu(x, y, puskuri=puskurit and taso == 1)
    if taso == 0:
        s.kiikku = True
        return s
    d = koko / 4
    for dx, dy in [(-d, -d), (d, -d), (-d, d), (d, d)]:
        s.lapset.append(h_puu(x + dx, y + dy, koko / 2, taso - 1,
                              puskurit))
    return s
# @loppu rakenteet


def main() -> None:
    # @alku vertailu
    print("rakenne   johdinta mm   viive ps (min–max)   vinous ps")
    for nimi, juuri in [("ketju", ketju()),
                        ("H-puu", h_puu(500.0, 500.0, 1000.0, 2)),
                        ("H-puu+p", h_puu(500.0, 500.0, 1000.0, 2, True))]:
        v = [t * 1e12 for t in viiveet(juuri)]
        print(f"{nimi:8} {pituus(juuri) / 1000:12.2f} "
              f"{min(v):9.1f}–{max(v):6.1f} {max(v) - min(v):12.1f}")
    # @loppu vertailu


if __name__ == "__main__":
    main()
