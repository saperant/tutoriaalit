"""Kokoelmien idiomit."""

from collections import Counter, defaultdict, deque
from operator import itemgetter

# @alku dict
varasto = {"ruuvi": 120, "mutteri": 80}
print(varasto.get("naula", 0))             # oletusarvo ilman poikkeusta
varasto.setdefault("naula", 0)
varasto |= {"mutteri": 75, "levy": 4}      # yhdistäminen (3.9+)
print(sorted(varasto.items(), key=itemgetter(1), reverse=True)[:2])
# @loppu dict

# @alku ryhmittely
tilaukset = [("Ada", "kirja"), ("Bob", "kynä"), ("Ada", "lamppu"),
             ("Cia", "kirja"), ("Bob", "kirja")]
asiakkaittain: defaultdict[str, list[str]] = defaultdict(list)
for asiakas, tuote in tilaukset:
    asiakkaittain[asiakas].append(tuote)
print(dict(asiakkaittain))
suosituimmat = Counter(tuote for _, tuote in tilaukset)
print(suosituimmat.most_common(2))
# @loppu ryhmittely

# @alku joukot
oikeudet = {"luku", "kirjoitus"}
vaaditut = {"luku", "poisto"}
print(sorted(vaaditut - oikeudet), sorted(vaaditut & oikeudet))
print("luku" in oikeudet)                  # O(1), listassa O(n)
# @loppu joukot

# @alku deque
viimeisimmat: deque[str] = deque(maxlen=3)  # rengaspuskuri
for tapahtuma in ["kirjautui", "haki", "tallensi", "poisti", "poistui"]:
    viimeisimmat.append(tapahtuma)
print(list(viimeisimmat))
jono = deque(["a", "b", "c"])
jono.appendleft("alku")                    # O(1), listan insert(0) on O(n)
print(jono.popleft(), jono.pop())
# @loppu deque

# @alku lajittelu
henkilot = [("Ada", 36), ("Bob", 28), ("Cia", 36), ("Dan", 41)]
# Lajittelu on vakaa: ensin toissijaisen, sitten ensisijaisen avaimen mukaan
henkilot.sort(key=itemgetter(0))
henkilot.sort(key=itemgetter(1), reverse=True)
print(henkilot)
# @loppu lajittelu
