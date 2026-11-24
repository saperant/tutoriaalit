"""Relaatioiden ominaisuudet, ekvivalenssiluokat ja sulkeuma."""

from collections import defaultdict
from collections.abc import Callable

Relaatio = Callable[[str, str], bool]


# @alku ominaisuudet
def ominaisuudet(joukko: list[str], r: Relaatio) -> list[str]:
    tulos = []
    if all(r(a, a) for a in joukko):
        tulos.append("refleksiivinen")
    if all(r(b, a) for a in joukko for b in joukko if r(a, b)):
        tulos.append("symmetrinen")
    if all(a == b for a in joukko for b in joukko if r(a, b) and r(b, a)):
        tulos.append("antisymmetrinen")
    if all(r(a, c) for a in joukko for b in joukko for c in joukko
           if r(a, b) and r(b, c)):
        tulos.append("transitiivinen")
    return tulos


sanat = ["kissa", "sakki", "aski", "kissat", "saki", "kassi"]
relaatiot: dict[str, Relaatio] = {
    "sama pituus": lambda a, b: len(a) == len(b),
    "anagrammi": lambda a, b: sorted(a) == sorted(b),
    "alkuosa (a on b:n alku)": lambda a, b: b.startswith(a),
    "eri sana": lambda a, b: a != b,
}
for nimi, r in relaatiot.items():
    print(f"{nimi}: {', '.join(ominaisuudet(sanat, r)) or '-'}")
# @loppu ominaisuudet

# @alku luokat
# Ekvivalenssirelaatio jakaa joukon luokkiin. Luokan edustajaksi
# kelpaa avain, joka on sama täsmälleen ekvivalenteille alkioille.
luokat: defaultdict[str, list[str]] = defaultdict(list)
for sana in sanat:
    luokat["".join(sorted(sana))].append(sana)
for avain, jasenet in sorted(luokat.items()):
    print(f"  [{avain}] {jasenet}")
# @loppu luokat

# @alku sulkeuma
# Transitiivinen sulkeuma Warshallin algoritmilla: kuka voi tavoittaa
# kenet suorien yhteyksien kautta?
asemat = ["Helsinki", "Tampere", "Oulu", "Turku", "Joensuu"]
suorat = {("Helsinki", "Tampere"), ("Tampere", "Oulu"),
          ("Turku", "Helsinki"), ("Joensuu", "Joensuu")}
n = len(asemat)
yhteys = [[(asemat[i], asemat[j]) in suorat for j in range(n)]
          for i in range(n)]
for k in range(n):
    for i in range(n):
        for j in range(n):
            yhteys[i][j] = yhteys[i][j] or (yhteys[i][k] and yhteys[k][j])
for i, a in enumerate(asemat):
    kohteet = [asemat[j] for j in range(n) if yhteys[i][j]]
    print(f"  {a:<9} -> {', '.join(kohteet) or '-'}")
# @loppu sulkeuma
