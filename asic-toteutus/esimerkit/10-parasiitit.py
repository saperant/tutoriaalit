"""Parasiittien poiminta: johtimen R ja C sen geometriasta.

Reitityksen jälkeen jokainen johdin on joukko suorakulmioita
metallikerroksilla. Poiminta laskee jokaiselle palalle vastuksen
(kerroksen neliövastus × pituus / leveys) ja kapasitanssin (pohja,
reunat ja naapurijohtimet) ja kirjoittaa ne SPEF-muodossa
ajoitusanalyysille. Viive nieluille lasketaan Elmore-mallilla.
"""

from dataclasses import dataclass

# @alku kerrokset
@dataclass(frozen=True)
class Kerros:
    r_nelio: float        # Ω/neliö
    c_pohja: float        # fF/µm², pohja ja katto yhteensä
    c_reuna: float        # fF/µm reunaa kohden
    c_naapuri: float      # fF/µm, naapuri vähimmäisvälin päässä


KERROKSET = {
    "met1": Kerros(0.125, 0.060, 0.040, 0.085),
    "met2": Kerros(0.125, 0.036, 0.036, 0.085),
    "met3": Kerros(0.047, 0.030, 0.034, 0.090),
}
R_VIA = 4.5               # Ω, yksi läpivienti
# @loppu kerrokset


# @alku pala
@dataclass
class Pala:
    """Johdinpala solmusta `mista` solmuun `mihin`."""
    mista: str
    mihin: str
    kerros: str
    pituus: float         # µm
    leveys: float         # µm
    naapuria: float = 0.0  # µm, matka vähimmäisvälillä naapurin vieressä
    via: bool = False     # pala alkaa läpiviennillä

    def r(self) -> float:
        k = KERROKSET[self.kerros]
        return k.r_nelio * self.pituus / self.leveys + R_VIA * self.via

    def c_maahan(self) -> float:
        k = KERROKSET[self.kerros]
        return (k.c_pohja * self.pituus * self.leveys
                + 2 * k.c_reuna * self.pituus)

    def c_kytkenta(self) -> float:
        return KERROKSET[self.kerros].c_naapuri * self.naapuria
# @loppu pala


# @alku elmore
def elmore(palat: list[Pala], nielut: dict[str, float], r_ajuri: float
           ) -> dict[str, float]:
    """Elmore-viive (ps) jokaiselle nielulle. Palan kapasitanssi
    jaetaan puoliksi sen päihin (π-malli); nielun pinni lisätään."""
    c = dict.fromkeys(["ajuri"] + [p.mihin for p in palat], 0.0)
    for p in palat:
        puoli = (p.c_maahan() + p.c_kytkenta()) / 2
        c[p.mista] += puoli
        c[p.mihin] += puoli
    for nielu, pinni in nielut.items():
        c[nielu] += pinni

    def alavirta(solmu: str) -> float:
        return c[solmu] + sum(alavirta(p.mihin) for p in palat
                              if p.mista == solmu)

    viive = {"ajuri": r_ajuri * alavirta("ajuri") * 1e-3}
    for p in palat:                         # palat juuresta lehtiin
        viive[p.mihin] = viive[p.mista] + p.r() * alavirta(p.mihin) * 1e-3
    return {n: viive[n] for n in nielut}
# @loppu elmore


def spef(nimi: str, palat: list[Pala]) -> list[str]:
    yht = sum(p.c_maahan() + p.c_kytkenta() for p in palat)
    rivit = [f"*D_NET {nimi} {yht:.2f}", "*CAP"]
    for i, p in enumerate(palat, 1):
        rivit.append(f"{i} {nimi}:{p.mihin} {p.c_maahan():.2f}")
    kytketyt = [p for p in palat if p.naapuria]
    for i, p in enumerate(kytketyt, len(palat) + 1):
        rivit.append(f"{i} {nimi}:{p.mihin} naapuri:1 "
                     f"{p.c_kytkenta():.2f}")
    rivit.append("*RES")
    for i, p in enumerate(palat, 1):
        rivit.append(f"{i} {nimi}:{p.mista} {nimi}:{p.mihin} {p.r():.1f}")
    return rivit + ["*END"]


def main() -> None:
    # @alku ajo
    # Reititetty johdin: ajurilta runkoa pitkin kahdelle nielulle.
    palat = [
        Pala("ajuri", "a", "met1", 12.0, 0.14),
        Pala("a", "b", "met2", 180.0, 0.14, naapuria=120.0, via=True),
        Pala("b", "n1", "met1", 15.0, 0.14, via=True),
        Pala("b", "c", "met3", 260.0, 0.30, via=True),
        Pala("c", "n2", "met1", 20.0, 0.14, via=True),
    ]
    nielut = {"n1": 2.0, "n2": 2.0}             # pinnit fF
    print("pala      kerros  pituus µm    R Ω   C fF  kytkentä fF")
    for p in palat:
        print(f"{p.mista + '-' + p.mihin:9} {p.kerros:6} {p.pituus:9.0f} "
              f"{p.r():7.1f} {p.c_maahan():6.2f} {p.c_kytkenta():10.2f}")
    c_johdin = sum(p.c_maahan() + p.c_kytkenta() for p in palat)
    arvio = 1.0 * (1 + len(nielut))             # luvun 4 johdinarvio fF
    print(f"johdin yhteensä {sum(p.r() for p in palat):.0f} Ω, "
          f"{c_johdin:.1f} fF; arvio ennen sijoittelua {arvio:.1f} fF")
    for r_ajuri, nimi in [(5800.0, "INV_X1"), (1450.0, "BUF_X4")]:
        v = elmore(palat, nielut, r_ajuri)
        print(f"ajuri {nimi}: viive n1 {v['n1']:.0f} ps, n2 "
              f"{v['n2']:.0f} ps")
    print("SPEF-ote:")
    for rivi in spef("summa", palat):
        print("  " + rivi)
    # @loppu ajo


if __name__ == "__main__":
    main()
