"""Monikko: kiinteä, muuttumaton arvoryhmä."""


def pienin_ja_suurin(luvut: list[float]) -> tuple[float, float]:
    """Palauttaa kaksi arvoa monikkona."""
    return min(luvut), max(luvut)


sijainti = (60.17, 24.94)            # leveys- ja pituuspiiri
leveys, pituus = sijainti            # purku kahteen nimeen
print(f"{leveys} N, {pituus} E")

alin, ylin = pienin_ja_suurin([-3.5, 4.0, 12.5, 7.0])
print(f"Lämpötilat {alin}–{ylin} °C")

# Monikko käy sanakirjan avaimeksi, lista ei.
etaisyydet = {("Helsinki", "Tampere"): 178, ("Helsinki", "Oulu"): 607}
print(etaisyydet[("Helsinki", "Oulu")], "km")
