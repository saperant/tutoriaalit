"""Kuka tuntee minkäkin osan: omistajuus ja bussikerroin historiasta."""

from collections import Counter

from historia import lue_loki, luo_repositorio
from organisaatio import OMINAISUUDET, OSAT

TUNTIJAN_OSUUS = 0.25     # vähintään neljännes osan muutoksista

luo_repositorio()
historia = lue_loki()

# @alku osuudet
# Jokaiselle osalle: kuinka monta muutosta kukin tekijä on tehnyt.
tekijat: dict[str, Counter[str]] = {osa: Counter() for osa in OSAT}
for muutos in historia:
    for osa in muutos.osat:
        tekijat[osa][muutos.tekija] += 1

print("ominaisuus  muutoksia  suurin tekijä")
for ominaisuus in OMINAISUUDET:
    yhteensa: Counter[str] = Counter()
    for osa in OSAT:
        if osa.startswith(ominaisuus):
            yhteensa += tekijat[osa]
    nimi, maara = yhteensa.most_common(1)[0]
    print(f"{ominaisuus:10}{yhteensa.total():>11}  {nimi} "
          f"{maara / yhteensa.total():.0%}")
# @loppu osuudet


# @alku bussikerroin
def tuntijat(osa: str) -> set[str]:
    kaikki = tekijat[osa].total()
    return {nimi for nimi, maara in tekijat[osa].items()
            if maara / kaikki >= TUNTIJAN_OSUUS}


def bussikerroin() -> list[str]:
    """Ahne arvio: poistetaan aina se, joka tuntee eniten osia, kunnes
    yli puolella osista ei ole enää yhtään tuntijaa."""
    jaljella = {osa: tuntijat(osa) for osa in OSAT}
    poistetut: list[str] = []
    while sum(not t for t in jaljella.values()) * 2 <= len(OSAT):
        laskuri = Counter(nimi for t in jaljella.values() for nimi in t)
        nimi = min(laskuri, key=lambda n: (-laskuri[n], n))
        poistetut.append(nimi)
        for t in jaljella.values():
            t.discard(nimi)
    return poistetut
# @loppu bussikerroin


yksin = sorted(osa for osa in OSAT if len(tuntijat(osa)) == 1)
print(f"osia, joilla on vain yksi tuntija: {len(yksin)}")
for osa in yksin:
    print(f"  {osa}: {next(iter(tuntijat(osa)))}")
poistetut = bussikerroin()
print(f"bussikerroin {len(poistetut)}: {', '.join(poistetut)}")
