"""Juurellinen puu: hakemistorakenne, syvyys, korkeus ja lehdet."""

from dataclasses import dataclass, field


# @alku solmu
@dataclass
class Solmu:
    nimi: str
    lapset: list["Solmu"] = field(default_factory=list)
    koko: int = 0                     # tiedoston koko tavuina

    def korkeus(self) -> int:
        """Pisimmän juuresta lehteen kulkevan polun kaarten määrä."""
        return max((1 + lapsi.korkeus() for lapsi in self.lapset), default=0)

    def lehdet(self) -> int:
        return 1 if not self.lapset else sum(lapsi.lehdet()
                                             for lapsi in self.lapset)

    def yhteiskoko(self) -> int:
        return self.koko + sum(lapsi.yhteiskoko() for lapsi in self.lapset)

    def tulosta(self, syvyys: int = 0) -> None:
        print("  " * syvyys + self.nimi)
        for lapsi in self.lapset:
            lapsi.tulosta(syvyys + 1)
# @loppu solmu


# @alku kaytto
projekti = Solmu("projekti", [
    Solmu("src", [Solmu("main.py", koko=1200),
                  Solmu("apu", [Solmu("io.py", koko=800),
                                Solmu("laskenta.py", koko=2400)])]),
    Solmu("tests", [Solmu("test_main.py", koko=600)]),
    Solmu("README.md", koko=300),
])
projekti.tulosta()
print("korkeus:", projekti.korkeus(), " lehtiä:", projekti.lehdet(),
      " koko:", projekti.yhteiskoko(), "tavua")


def solmuja(s: Solmu) -> int:
    return 1 + sum(solmuja(lapsi) for lapsi in s.lapset)


# Jokaisella solmulla paitsi juurella on yksi vanhempi: kaaria n - 1.
print("solmuja:", solmuja(projekti), " kaaria:", solmuja(projekti) - 1)
# @loppu kaytto
