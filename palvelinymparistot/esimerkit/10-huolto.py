"""Kubernetes-solmujen huolto: tyhjennys PodDisruptionBudgetin rajoissa.

Ennen ytimen päivitystä solmu tyhjennetään (kubectl drain). Tyhjennys
ei saa pudottaa sovelluksen käytettävissä olevien kopioiden määrää
alle sen PodDisruptionBudgetin (PDB) minAvailable-arvon. Funktio
tarkistaa, minkä solmujen tyhjennys on turvallista nyt.
"""

from collections import Counter

# Sovellus -> PDB:n minAvailable
PDB = {"verkkokauppa": 2, "haku": 2, "tilaukset": 1}

# Solmu -> sillä ajossa olevat podit (sovelluksen nimellä)
SIJOITTELU = {
    "solmu-a": ["verkkokauppa", "haku", "tilaukset"],
    "solmu-b": ["verkkokauppa", "haku"],
    "solmu-c": ["verkkokauppa", "tilaukset"],
}


# @alku tyhjennys
def esteet(solmu: str, sijoittelu: dict[str, list[str]],
           pdb: dict[str, int]) -> list[str]:
    """Sovellukset, joiden PDB rikkoutuisi, jos solmu tyhjennetään."""
    kaikki = Counter(p for podit in sijoittelu.values() for p in podit)
    poistuvat = Counter(sijoittelu[solmu])
    return sorted(sovellus for sovellus, kpl in poistuvat.items()
                  if kaikki[sovellus] - kpl < pdb.get(sovellus, 0))
# @loppu tyhjennys


def raportti() -> None:
    for solmu in SIJOITTELU:
        estavat = esteet(solmu, SIJOITTELU, PDB)
        print(f"  {solmu}: " + ("voi tyhjentää" if not estavat else
                                "odota, PDB estää: " + ", ".join(estavat)))


def main() -> None:
    print("alussa:")
    raportti()
    SIJOITTELU["solmu-c"].append("haku")
    print("kun haulla on kolmas kopio solmulla solmu-c:")
    raportti()


if __name__ == "__main__":
    main()
