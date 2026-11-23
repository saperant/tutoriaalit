"""Ostoskori dataluokilla: luokka koostuu toisista olioista."""

from dataclasses import dataclass, field


@dataclass
class Tuote:
    nimi: str
    hinta_snt: int


@dataclass
class Rivi:
    tuote: Tuote
    maara: int

    def hinta(self) -> int:
        return self.tuote.hinta_snt * self.maara


@dataclass
class Ostoskori:
    rivit: list[Rivi] = field(default_factory=list)

    def lisaa(self, tuote: Tuote, maara: int = 1) -> None:
        """Lisää tuotteen. Sama tuote kasvattaa olemassa olevaa riviä."""
        for rivi in self.rivit:
            if rivi.tuote == tuote:
                rivi.maara += maara
                return
        self.rivit.append(Rivi(tuote, maara))

    def yhteensa(self) -> int:
        return sum(rivi.hinta() for rivi in self.rivit)


kahvi = Tuote("Kahvi 500 g", 699)
pulla = Tuote("Korvapuusti", 150)
kori = Ostoskori()
kori.lisaa(kahvi)
kori.lisaa(pulla, 4)
kori.lisaa(pulla, 2)
for rivi in kori.rivit:
    print(f"{rivi.tuote.nimi:<14}{rivi.maara:>3} kpl{rivi.hinta():>6} snt")
print(f"Yhteensä {kori.yhteensa()} snt")
print(kahvi)                                  # dataclass tekee __repr__:n
print(kahvi == Tuote("Kahvi 500 g", 699))     # ja vertailun
