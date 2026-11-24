"""Kirjautumisyritysten rajoitus: kasvava viive tilikohtaisesti."""

from collections import defaultdict


# @alku rajoitin
class Rajoitin:
    """Viisi epäonnistumista sallitaan, sitten viive kaksinkertaistuu.
    Pysyvä lukitus antaisi hyökkääjälle keinon lukita kenen tahansa tili
    (palvelunesto), joten viive on parempi oletus."""

    def __init__(self, vapaat: int = 5, perusviive: float = 1.0) -> None:
        self.vapaat = vapaat
        self.perusviive = perusviive
        self.virheet: dict[str, int] = defaultdict(int)
        self.seuraava: dict[str, float] = defaultdict(float)

    def saa_yrittaa(self, tili: str, nyt: float) -> bool:
        return nyt >= self.seuraava[tili]

    def kirjaa(self, tili: str, onnistui: bool, nyt: float) -> None:
        if onnistui:
            self.virheet.pop(tili, None)
            self.seuraava.pop(tili, None)
            return
        self.virheet[tili] += 1
        yli = self.virheet[tili] - self.vapaat
        if yli > 0:
            self.seuraava[tili] = nyt + self.perusviive * 2 ** (yli - 1)
# @loppu rajoitin


r = Rajoitin()
nyt = 0.0
estetyt = 0
for _ in range(1000):                 # arvaushyökkäys yhteen tiliin
    if r.saa_yrittaa("aino", nyt):
        r.kirjaa("aino", onnistui=False, nyt=nyt)
    else:
        estetyt += 1
    nyt += 0.1                        # kymmenen yritystä sekunnissa
print(f"virheellisiä yrityksiä: {r.virheet['aino']}, estettyjä: {estetyt}")
print(f"seuraava sallittu yritys {r.seuraava['aino'] - nyt:.0f} s päästä")
