"""Yhteinen työaika ja kysymyksen kiertoaika toimipaikkojen välillä.

Erot UTC-aikaan ovat talviajan mukaisia ja kiinteitä, jotta tulos ei
riipu ajopäivästä. Kesäaika siirtää eroja tunnilla eri päivinä eri
maissa.
"""

from itertools import combinations, product

UTC_ERO = {"Helsinki": 2.0, "Lontoo": 0.0, "New York": -5.0,
           "Bengaluru": 5.5, "San Francisco": -8.0}
ALKAA, PAATTYY = 9.0, 17.0      # työpäivä paikallista aikaa


# @alku yhteinen
def tyoaika_utc(paikka: str) -> tuple[float, float]:
    return ALKAA - UTC_ERO[paikka], PAATTYY - UTC_ERO[paikka]


def yhteinen(paikat: tuple[str, ...]) -> float:
    """Tunnit, jolloin kaikki paikat ovat töissä yhtä aikaa. Työpäivä
    toistuu vuorokauden välein, joten muita paikkoja kokeillaan myös
    vuorokautta aiemmin ja myöhemmin."""
    paras = 0.0
    for siirrot in product((-24.0, 0.0, 24.0), repeat=len(paikat) - 1):
        alku, loppu = tyoaika_utc(paikat[0])
        for paikka, siirto in zip(paikat[1:], siirrot, strict=True):
            a, b = tyoaika_utc(paikka)
            alku, loppu = max(alku, a + siirto), min(loppu, b + siirto)
        paras = max(paras, loppu - alku)
    return paras
# @loppu yhteinen


# @alku kierto
def seuraava_tyohetki(paikka: str, utc: float) -> float:
    """Hetki itse, jos paikassa ollaan töissä, muuten seuraava aamu."""
    alku, loppu = tyoaika_utc(paikka)
    paiva = (utc - alku) // 24
    alku, loppu = alku + 24 * paiva, loppu + 24 * paiva
    return utc if utc < loppu else alku + 24


def kiertoaika(kysyja: str, vastaaja: str, kello: float) -> float:
    """Kysymys lähtee kysyjän kellon mukaan. Vastaaja vastaa tunnin
    kuluttua siitä, kun on töissä. Montako tuntia kuluu, ennen kuin
    kysyjä on töissä ja voi lukea vastauksen?"""
    lahtee = kello - UTC_ERO[kysyja]
    vastaus = seuraava_tyohetki(vastaaja, lahtee) + 1
    return seuraava_tyohetki(kysyja, vastaus) - lahtee
# @loppu kierto


print("yhteistä työaikaa päivässä:")
for pari in combinations(UTC_ERO, 2):
    print(f"  {pari[0]:9} - {pari[1]:14}{yhteinen(pari):5.1f} h")
kolmikko = ("Helsinki", "Lontoo", "New York")
print(f"  {', '.join(kolmikko)}: {yhteinen(kolmikko):.1f} h")
print("kysymyksen kiertoaika Helsingistä:  klo 9  klo 16")
for vastaaja in ("Lontoo", "Bengaluru", "New York", "San Francisco"):
    aamu = kiertoaika("Helsinki", vastaaja, 9.0)
    ilta = kiertoaika("Helsinki", vastaaja, 16.0)
    print(f"  {vastaaja:33}{aamu:5.0f} h{ilta:6.0f} h")
