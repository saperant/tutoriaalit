"""Topologinen järjestys: käännösjärjestys riippuvuuksista (Kahn)."""

from collections import deque

Riippuvuudet = dict[str, list[str]]


# @alku kahn
def kaannosjarjestys(riippuu: Riippuvuudet) -> list[str]:
    """Moduulit järjestyksessä, jossa riippuvuudet tulevat ensin.

    Riippuvuussuhde on osittainen järjestys vain, jos siinä ei ole
    kehää; kehä aiheuttaa ValueErrorin.
    """
    moduulit = set(riippuu) | {d for ds in riippuu.values() for d in ds}
    odottaa = {m: len(riippuu.get(m, [])) for m in moduulit}
    tarvitsijat: dict[str, list[str]] = {m: [] for m in moduulit}
    for m, ds in riippuu.items():
        for d in ds:
            tarvitsijat[d].append(m)
    valmiit = deque(sorted(m for m, n in odottaa.items() if n == 0))
    jarjestys = []
    while valmiit:
        m = valmiit.popleft()
        jarjestys.append(m)
        for t in sorted(tarvitsijat[m]):
            odottaa[t] -= 1
            if odottaa[t] == 0:
                valmiit.append(t)
    if len(jarjestys) != len(moduulit):
        jaljella = sorted(m for m in moduulit if odottaa[m] > 0)
        raise ValueError(f"riippuvuuskehä: {jaljella}")
    return jarjestys
# @loppu kahn


# @alku kaytto
projekti: Riippuvuudet = {
    "sovellus": ["kayttoliittyma", "tietokanta"],
    "kayttoliittyma": ["grafiikka", "apu"],
    "tietokanta": ["apu"],
    "grafiikka": ["apu"],
}
print("järjestys:", " -> ".join(kaannosjarjestys(projekti)))

projekti["apu"] = ["sovellus"]           # joku lisää kehän
try:
    kaannosjarjestys(projekti)
except ValueError as virhe:
    print("virhe:", virhe)
# @loppu kaytto
