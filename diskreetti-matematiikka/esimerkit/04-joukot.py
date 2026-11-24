"""Joukko-operaatiot, potenssijoukko ja karteesinen tulo."""

from itertools import chain, combinations, product

# @alku operaatiot
python = {"Aino", "Olli", "Pekka", "Sanna"}
c_kieli = {"Olli", "Sanna", "Timo"}
kaikki = python | c_kieli | {"Ulla"}          # perusjoukko U

print("molemmat  A ∩ B:", sorted(python & c_kieli))
print("jompikumpi A ∪ B:", sorted(python | c_kieli))
print("vain Python A - B:", sorted(python - c_kieli))
print("täsmälleen yksi A △ B:", sorted(python ^ c_kieli))
print("ei kumpaakaan:", sorted(kaikki - (python | c_kieli)))
# De Morganin laki joukoille: (A ∪ B)' = A' ∩ B'
print("De Morgan:",
      kaikki - (python | c_kieli) == (kaikki - python) & (kaikki - c_kieli))
print("osajoukko {Olli} ⊆ A:", {"Olli"} <= python)
# @loppu operaatiot


# @alku potenssijoukko
def potenssijoukko(joukko: set[str]) -> list[frozenset[str]]:
    """Kaikki osajoukot; niitä on 2^|joukko|."""
    alkiot = sorted(joukko)
    return [frozenset(c) for c in chain.from_iterable(
        combinations(alkiot, k) for k in range(len(alkiot) + 1))]


oikeudet = {"luku", "kirjoitus", "suoritus"}
osajoukot = potenssijoukko(oikeudet)
print(f"{len(osajoukot)} oikeusyhdistelmää = 2^{len(oikeudet)}")
for o in osajoukot:
    print("  {" + ", ".join(sorted(o)) + "}")
# @loppu potenssijoukko

# @alku tulo
koot = ["S", "M", "L"]
varit = ["musta", "valkoinen"]
variantit = list(product(koot, varit))      # koot × värit
print(f"|koot × värit| = {len(koot)}·{len(varit)} = {len(variantit)}")
print("ensimmäiset:", variantit[:3])
# @loppu tulo
