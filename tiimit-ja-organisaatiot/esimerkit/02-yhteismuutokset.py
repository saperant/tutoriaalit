"""Mitkä osat muuttuvat yhdessä ja montako tiimiä yksi muutos vaatii."""

from collections import Counter
from itertools import combinations

from historia import lue_loki, luo_repositorio
from organisaatio import JAOT

luo_repositorio()
historia = lue_loki()

# @alku parit
# Kytkentäaste: kuinka suuressa osassa harvemmin muuttuvan osan
# muutoksista myös toinen osa muuttui.
kerrat = Counter(osa for m in historia for osa in m.osat)
yhdessa = Counter(pari for m in historia
                  for pari in combinations(sorted(m.osat), 2))


def aste(pari: tuple[str, str]) -> float:
    return yhdessa[pari] / min(kerrat[pari[0]], kerrat[pari[1]])


print("useimmin yhdessä muuttuvat osat:")
for pari in sorted(yhdessa, key=lambda p: (-yhdessa[p], p))[:6]:
    print(f"  {pari[0]:11} {pari[1]:11} {yhdessa[pari]:3} kertaa, "
          f"kytkentäaste {aste(pari):.2f}")
# @loppu parit

# @alku tiimit
print("muutoksen vaatimat tiimit:")
for nimi, jako in JAOT.items():
    tiimeja = [len({jako(osa) for osa in m.osat}) for m in historia]
    usea = sum(t > 1 for t in tiimeja)
    print(f"  {nimi:18} usean tiimin muutoksia "
          f"{usea / len(tiimeja):4.0%}, keskimäärin "
          f"{sum(tiimeja) / len(tiimeja):.2f} tiimiä")
# @loppu tiimit
