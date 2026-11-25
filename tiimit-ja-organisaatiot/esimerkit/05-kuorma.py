"""Karkea mittari tiimin kognitiiviselle kuormalle."""

from dataclasses import dataclass

# Alueen vaativuus pisteinä: yksinkertainen, mutkikas, kompleksinen.
PISTEET = {"yksinkertainen": 1, "mutkikas": 2, "kompleksinen": 3}
ALUERAJA = 3            # esim. kolme yksinkertaista tai yksi kompleksinen
TEKNIIKKARAJA = 5


@dataclass(frozen=True)
class Tiimi:
    nimi: str
    alueet: dict[str, str]         # alue -> vaativuus
    tekniikat: tuple[str, ...]
    paivystaa: bool


# @alku tiimit
TIIMIT = [
    Tiimi("hakutiimi", {"haku": "mutkikas",
                        "tuoteluettelo": "yksinkertainen"},
          ("Python", "PostgreSQL", "OpenSearch", "React"), False),
    Tiimi("ostotiimi", {"kori": "yksinkertainen",
                        "kampanjat": "yksinkertainen",
                        "hinnoittelu": "mutkikas"},
          ("Python", "PostgreSQL", "Redis", "React"), False),
    Tiimi("tilaustiimi", {"tilaukset": "mutkikas", "toimitus": "mutkikas"},
          ("Java", "PostgreSQL", "Kafka", "React"), True),
    Tiimi("maksutiimi", {"maksut": "kompleksinen"},
          ("Java", "PostgreSQL", "Kafka", "React", "HSM", "COBOL-silta"),
          True),
]
# @loppu tiimit


# @alku mittari
def arvio(tiimi: Tiimi) -> tuple[int, list[str]]:
    pisteet = sum(PISTEET[v] for v in tiimi.alueet.values())
    huomiot = []
    if pisteet > ALUERAJA:
        huomiot.append("liikaa alueita")
    mutkikkaita = sum(v == "mutkikas" for v in tiimi.alueet.values())
    if mutkikkaita > 1:
        huomiot.append("kaksi mutkikasta aluetta")
    if len(tiimi.tekniikat) > TEKNIIKKARAJA:
        huomiot.append("laaja tekniikkakirjo")
    if tiimi.paivystaa and pisteet >= ALUERAJA:
        huomiot.append("päivystys täyden kuorman päällä")
    return pisteet, huomiot
# @loppu mittari


print(f"{'tiimi':13}{'aluepisteet':>12}{'tekniikoita':>13}")
for tiimi in TIIMIT:
    pisteet, huomiot = arvio(tiimi)
    print(f"{tiimi.nimi:13}{pisteet:>12}{len(tiimi.tekniikat):>13}")
    for huomio in huomiot:
        print(f"  - {huomio}")
