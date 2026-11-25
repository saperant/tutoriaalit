"""Parittainen testaus: pieni testijoukko, joka kattaa kaikki arvoparit."""

from itertools import combinations, product

Parametrit = dict[str, list[str]]
Tapaus = dict[str, str]
Pari = tuple[tuple[str, str], tuple[str, str]]


# @alku parit
def kaikki_parit(parametrit: Parametrit) -> set[Pari]:
    """Jokaisen kahden parametrin jokainen arvoyhdistelmä."""
    parit = set()
    for a, b in combinations(parametrit, 2):
        for x, y in product(parametrit[a], parametrit[b]):
            parit.add(((a, x), (b, y)))
    return parit


def tapauksen_parit(tapaus: Tapaus) -> set[Pari]:
    return set(combinations(tapaus.items(), 2))


def parittaiset(parametrit: Parametrit) -> list[Tapaus]:
    """Ahne valinta: aina tapaus, joka kattaa eniten uusia pareja."""
    kattamatta = kaikki_parit(parametrit)
    ehdokkaat = [dict(zip(parametrit, arvot, strict=True))
                 for arvot in product(*parametrit.values())]
    valitut = []
    while kattamatta:
        paras = max(ehdokkaat,
                    key=lambda t: len(tapauksen_parit(t) & kattamatta))
        valitut.append(paras)
        kattamatta -= tapauksen_parit(paras)
    return valitut
# @loppu parit
