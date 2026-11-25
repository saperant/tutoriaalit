"""CODEOWNERS-tiedoston jäsennys ja kattavuuden tarkistus.

Säännöistä tuetaan osajoukko: *, *.pääte, /hakemisto/ ja /polku/tiedosto.
Kuten GitHubissa ja GitLabissa, viimeinen osuva sääntö voittaa.
"""

from fnmatch import fnmatch

# @alku tiedosto
CODEOWNERS = """\
# Dokumentit hakemistosta riippumatta, muut hakemistoittain.
*.md            @kauppa/dokumentointi
/haku/          @kauppa/hakutiimi
/kori/          @kauppa/ostotiimi
/tilaus/        @kauppa/tilaustiimi
/maksu/         @pekka
/maksu/ui.py    @kauppa/maksutiimi @pekka
/toimitus/      @kauppa/tilaustiimi
"""
# @loppu tiedosto

TIEDOSTOT = [f"{o}/{k}.py" for o in ("haku", "kori", "tilaus", "maksu")
             for k in ("ui", "api", "db")]
TIEDOSTOT += ["README.md", "haku/README.md", "infra/putki.yaml",
              "infra/tietokanta.tf"]


# @alku jasennys
def saannot(teksti: str) -> list[tuple[str, list[str]]]:
    tulos = []
    for rivi in teksti.splitlines():
        osat = rivi.split("#")[0].split()
        if osat:
            tulos.append((osat[0], osat[1:]))
    return tulos


def osuu(malli: str, polku: str) -> bool:
    if malli.endswith("/"):                  # hakemisto sisältöineen
        return polku.startswith(malli.lstrip("/"))
    if malli.startswith("/"):                # polku repositorion juuresta
        return fnmatch(polku, malli[1:])
    return fnmatch(polku.rsplit("/", 1)[-1], malli)   # nimi missä tahansa


def omistajat(polku: str, lista: list[tuple[str, list[str]]]) -> list[str]:
    """Viimeinen osuva sääntö voittaa."""
    for malli, nimet in reversed(lista):
        if osuu(malli, polku):
            return nimet
    return []
# @loppu jasennys


# @alku tarkistus
lista = saannot(CODEOWNERS)
ilman = [t for t in TIEDOSTOT if not omistajat(t, lista)]
print(f"tiedostoja {len(TIEDOSTOT)}, ilman omistajaa {len(ilman)}:")
for tiedosto in ilman:
    print(f"  {tiedosto}")

print("vain yhden henkilön varassa:")
for tiedosto in TIEDOSTOT:
    nimet = omistajat(tiedosto, lista)
    if nimet and all("/" not in nimi for nimi in nimet):
        print(f"  {tiedosto} {' '.join(nimet)}")

print("säännöt, jotka eivät osu mihinkään:")
for malli, _ in lista:
    if not any(osuu(malli, t) for t in TIEDOSTOT):
        print(f"  {malli}")
# @loppu tarkistus
