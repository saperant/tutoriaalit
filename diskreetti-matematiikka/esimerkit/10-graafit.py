"""Graafin esitystavat, asteet ja yhtenäiset komponentit."""

from collections import deque

# @alku esitys
radat = [("Helsinki", "Tampere"), ("Tampere", "Oulu"),
         ("Helsinki", "Turku"), ("Turku", "Tampere"),
         ("Tampere", "Pori"), ("Joensuu", "Nurmes")]
kaupungit = sorted({k for rata in radat for k in rata})

# Vierekkäisyyslistat: tila O(V + E), naapurit nopeasti.
naapurit: dict[str, list[str]] = {k: [] for k in kaupungit}
for a, b in radat:
    naapurit[a].append(b)
    naapurit[b].append(a)

# Vierekkäisyysmatriisi: tila O(V²), "onko kaari?" vakioajassa.
indeksi = {k: i for i, k in enumerate(kaupungit)}
matriisi = [[0] * len(kaupungit) for _ in kaupungit]
for a, b in radat:
    matriisi[indeksi[a]][indeksi[b]] = matriisi[indeksi[b]][indeksi[a]] = 1

for k in kaupungit:
    rivi = "".join(map(str, matriisi[indeksi[k]]))
    print(f"  {k:<9} {rivi}  naapurit: {', '.join(naapurit[k])}")
# @loppu esitys

# @alku asteet
# Kättelylemma: asteiden summa on kaksi kertaa kaarten määrä, joten
# paritonasteisia solmuja on parillinen määrä.
asteet = {k: len(naapurit[k]) for k in kaupungit}
print("asteiden summa:", sum(asteet.values()), "= 2 ·", len(radat))
print("paritonasteiset:", [k for k, a in asteet.items() if a % 2])
# @loppu asteet


# @alku komponentit
def komponentit(naapurit: dict[str, list[str]]) -> list[list[str]]:
    """Leveyshaku jokaisesta vielä käymättömästä solmusta."""
    nahty: set[str] = set()
    tulos = []
    for alku in sorted(naapurit):
        if alku in nahty:
            continue
        osa, jono = [], deque([alku])
        nahty.add(alku)
        while jono:
            s = jono.popleft()
            osa.append(s)
            for t in naapurit[s]:
                if t not in nahty:
                    nahty.add(t)
                    jono.append(t)
        tulos.append(sorted(osa))
    return tulos


for osa in komponentit(naapurit):
    print("komponentti:", osa)
# @loppu komponentit
