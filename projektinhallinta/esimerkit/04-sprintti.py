"""Sprintin sitoumus: kuinka usein keskinopeuteen mitoitettu sprintti
valmistuu kokonaan?

Nopeus on sprintissä valmistuneiden tarinapisteiden summa. Historia on
kahdentoista sprintin mittainen.
"""

import random
import statistics

NOPEUDET = [21, 34, 27, 18, 30, 25, 29, 16, 33, 24, 28, 22]


# @alku sitoumus
def osumisosuus(sitoumus: float, toistoja: int = 20_000) -> float:
    """Osuus sprinteistä, joissa nopeus riittää sitoumukseen, kun
    seuraavan sprintin nopeus arvotaan historiasta."""
    rng = random.Random(11)
    return sum(rng.choice(NOPEUDET) >= sitoumus
               for _ in range(toistoja)) / toistoja
# @loppu sitoumus


keskiarvo = statistics.mean(NOPEUDET)
jarjestetty = sorted(NOPEUDET)
print(f"keskinopeus {keskiarvo:.1f}, vaihteluväli "
      f"{jarjestetty[0]}-{jarjestetty[-1]}, keskihajonta "
      f"{statistics.stdev(NOPEUDET):.1f}")
print("sitoumus            pistettä   valmistuu kokonaan")
for nimi, sitoumus in [("paras sprintti", jarjestetty[-1]),
                       ("keskiarvo", keskiarvo),
                       ("alin neljännes", jarjestetty[len(NOPEUDET) // 4]),
                       ("huonoin sprintti", jarjestetty[0])]:
    print(f"{nimi:<19} {sitoumus:6.0f}      {osumisosuus(sitoumus):6.0%}")

# @alku eilinen
# "Eilisen sää": sitoudutaan siihen, mitä edellinen sprintti tuotti.
osumat = sum(nyt >= edellinen
             for edellinen, nyt in zip(NOPEUDET, NOPEUDET[1:], strict=False))
print(f"eilisen sää: {osumat}/{len(NOPEUDET) - 1} sprinttiä piti")
kolmen = [statistics.mean(NOPEUDET[i - 3:i]) for i in range(3, 12)]
osumat3 = sum(nyt >= ka
              for ka, nyt in zip(kolmen, NOPEUDET[3:], strict=True))
print(f"kolmen sprintin keskiarvo: {osumat3}/{len(kolmen)} piti")
# @loppu eilinen
