"""itertools: valmiit iteraattorirakenteet."""

import itertools
from collections.abc import Iterator

# @alku itertools
mittaukset = [3, 5, 4, 8, 12, 11, 15]

for era in itertools.batched(mittaukset, 3):       # 3.12
    print("erä", era)

muutokset = [b - a for a, b in itertools.pairwise(mittaukset)]
print("muutokset", muutokset)

print("kumulatiivinen", list(itertools.accumulate(mittaukset)))

tapahtumat = [("ma", "kirjaus"), ("ma", "haku"), ("ti", "haku")]
for paiva, ryhma in itertools.groupby(tapahtumat, key=lambda t: t[0]):
    print(paiva, [nimi for _, nimi in ryhma])
# @loppu itertools


# @alku aareton
def tunnisteet(etuliite: str) -> Iterator[str]:
    """Ääretön generaattori: arvot lasketaan vasta pyydettäessä."""
    for n in itertools.count(1):
        yield f"{etuliite}-{n:04d}"


print(list(itertools.islice(tunnisteet("TILAUS"), 3)))
# @loppu aareton
