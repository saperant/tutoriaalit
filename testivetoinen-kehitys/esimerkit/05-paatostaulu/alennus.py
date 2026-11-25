"""Tilauksen alennusprosentti päätöstaulun mukaan."""


# @alku alennus
def alennusprosentti(kanta_asiakas: bool, koodi: bool, iso: bool) -> int:
    """Alennukset eivät kasaannu: suurin yksittäinen alennus pätee.

    Kampanjakoodi antaa 10 %, kanta-asiakkuus 5 % ja vähintään 100
    euron tilaus 5 %. Poikkeus: kanta-asiakkaan iso tilaus saa 10 %,
    ja jos hänellä on lisäksi kampanjakoodi, 15 %.
    """
    if kanta_asiakas and koodi and iso:
        return 15
    if koodi or (kanta_asiakas and iso):
        return 10
    if kanta_asiakas or iso:
        return 5
    return 0
# @loppu alennus
