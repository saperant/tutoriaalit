"""Kvanttorit ohjelmassa: all() on ∀ ja any() on ∃."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Tilaus:
    numero: int
    asiakas: str
    rivit: tuple[int, ...]     # rivien hinnat senteissä


tilaukset = [
    Tilaus(1, "Aino", (1250, 399)),
    Tilaus(2, "Olli", ()),
    Tilaus(3, "Aino", (19900,)),
]

# @alku kvanttorit
# ∀t: t:llä on vähintään yksi rivi
print("kaikilla tilauksilla rivejä:", all(t.rivit for t in tilaukset))
# ∃t: t:n summa > 100 €
print("jokin yli 100 €:", any(sum(t.rivit) > 10000 for t in tilaukset))
# ¬∀t P(t)  ≡  ∃t ¬P(t): vastaesimerkki kertoo, mikä rikkoo väitteen
vastaesimerkit = [t.numero for t in tilaukset if not t.rivit]
print("vastaesimerkit:", vastaesimerkit)
# @loppu kvanttorit

# @alku tyhja
# Tyhjän joukon yli ∀ on aina tosi ja ∃ aina epätosi.
print("all([]) =", all([]), " any([]) =", any([]))
tyhja: list[Tilaus] = []
print("tyhjällä listalla 'kaikki maksettu':",
      all(sum(t.rivit) == 0 for t in tyhja))
# @loppu tyhja

# @alku sisakkaiset
# ∀a ∃t: asiakkaalla a on tilaus t   vs.   ∃t ∀a: ...
asiakkaat = ["Aino", "Olli", "Pekka"]
kaikilla_tilaus = all(any(t.asiakas == a for t in tilaukset)
                      for a in asiakkaat)
print("jokaisella asiakkaalla on tilaus:", kaikilla_tilaus)
ilman = [a for a in asiakkaat
         if not any(t.asiakas == a for t in tilaukset)]
print("ilman tilausta:", ilman)
# @loppu sisakkaiset
