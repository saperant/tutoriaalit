"""Graafin väritys: ahne algoritmi, kromaattinen luku ja kaksijakoisuus."""

from collections import deque
from itertools import product

# @alku ahne
# Tenttiaikataulu: kaari = yhteisiä opiskelijoita, väri = aikaväli.
ristiriidat = {
    "matikka": ["fysiikka", "ohjelmointi", "tilastot"],
    "fysiikka": ["matikka", "kemia"],
    "ohjelmointi": ["matikka", "tilastot", "kemia"],
    "kemia": ["fysiikka", "ohjelmointi"],
    "tilastot": ["matikka", "ohjelmointi"],
}


def ahne_varitys(naapurit: dict[str, list[str]],
                 jarjestys: list[str]) -> dict[str, int]:
    """Jokainen solmu saa pienimmän värin, jota naapureilla ei ole."""
    vari: dict[str, int] = {}
    for s in jarjestys:
        kaytetyt = {vari[t] for t in naapurit[s] if t in vari}
        vari[s] = next(c for c in range(len(naapurit)) if c not in kaytetyt)
    return vari


v = ahne_varitys(ristiriidat, sorted(ristiriidat))
print(f"tentit: {max(v.values()) + 1} aikaväliä:", v)

# Järjestys ratkaisee. Kruunugraafissa a_i ja b_j ovat naapureita, kun
# i ≠ j. Kaksi väriä riittää, mutta huono järjestys vaatii neljä.
kruunu = {f"{x}{i}": [f"{y}{j}" for j in range(1, 5) if j != i]
          for x, y in (("a", "b"), ("b", "a")) for i in range(1, 5)}
hyva = [f"a{i}" for i in range(1, 5)] + [f"b{i}" for i in range(1, 5)]
huono = [f"{x}{i}" for i in range(1, 5) for x in "ab"]
for nimi, jarjestys in (("ensin a:t", hyva), ("vuorotellen", huono)):
    v = ahne_varitys(kruunu, jarjestys)
    print(f"kruunu, {nimi}: {max(v.values()) + 1} väriä")
# @loppu ahne


# @alku tarkka
def kromaattinen_luku(naapurit: dict[str, list[str]]) -> int:
    """Pienin värimäärä kokeilemalla kaikki k^n väritystä."""
    solmut = sorted(naapurit)
    for k in range(1, len(solmut) + 1):
        for varit in product(range(k), repeat=len(solmut)):
            v = dict(zip(solmut, varit, strict=True))
            if all(v[s] != v[t] for s in solmut for t in naapurit[s]):
                return k
    return len(solmut)


print("kromaattinen luku:", kromaattinen_luku(ristiriidat))
# @loppu tarkka


# @alku kaksijakoinen
def kaksijakoinen(naapurit: dict[str, list[str]]) -> bool:
    """2-väritys leveyshaulla; pariton kehä estää sen."""
    puoli: dict[str, int] = {}
    for alku in naapurit:
        if alku in puoli:
            continue
        puoli[alku] = 0
        jono = deque([alku])
        while jono:
            s = jono.popleft()
            for t in naapurit[s]:
                if t not in puoli:
                    puoli[t] = 1 - puoli[s]
                    jono.append(t)
                elif puoli[t] == puoli[s]:
                    return False
    return True


print("tenttigraafi kaksijakoinen:", kaksijakoinen(ristiriidat))
nelio = {"a": ["b", "d"], "b": ["a", "c"], "c": ["b", "d"], "d": ["c", "a"]}
print("neliö (parillinen kehä) kaksijakoinen:", kaksijakoinen(nelio))
# @loppu kaksijakoinen
