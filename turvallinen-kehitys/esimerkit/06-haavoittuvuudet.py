"""Riippuvuuksien vertailu haavoittuvuustietoon (OSV-muoto).

OSV (Open Source Vulnerabilities) kuvaa haavoittuvuuden paketteina ja
versioväleinä. Tarkistus on yksinkertainen vertailu, mutta sen rajat on
tunnettava: tietokanta ei tiedä, käytetäänkö haavoittuvaa funktiota,
eikä se tunne haavoittuvuuksia, joita ei ole vielä julkaistu.
"""

from dataclasses import dataclass

Versio = tuple[int, ...]


def versio(s: str) -> Versio:
    return tuple(int(osa) for osa in s.split("."))


# @alku tieto
@dataclass(frozen=True)
class Tiedote:
    tunnus: str
    paketti: str
    alkaen: str          # "introduced"
    korjattu: str | None  # "fixed"; None = korjausta ei ole


TIEDOTTEET = (
    Tiedote("ESIM-2024-0001", "requests", "2.3.0", "2.32.0"),
    Tiedote("ESIM-2023-0002", "urllib3", "2.0.0", "2.0.6"),
    Tiedote("ESIM-2024-0003", "jinja2", "0.1", "3.1.4"),
    Tiedote("ESIM-2025-0004", "pyyaml", "6.0", None),
)
# @loppu tieto


# @alku vertailu
def osuu(t: Tiedote, nimi: str, ver: str) -> bool:
    if t.paketti != nimi or versio(ver) < versio(t.alkaen):
        return False
    return t.korjattu is None or versio(ver) < versio(t.korjattu)


def raportti(paketit: dict[str, str]) -> list[str]:
    rivit = []
    for nimi, ver in sorted(paketit.items()):
        for t in TIEDOTTEET:
            if osuu(t, nimi, ver):
                toimenpide = (f"päivitä >= {t.korjattu}" if t.korjattu
                              else "ei korjausta: arvioi käyttö ja rajaa")
                rivit.append(f"{t.tunnus} {nimi} {ver}: {toimenpide}")
    return rivit
# @loppu vertailu


def main() -> None:
    lukitus = {"requests": "2.31.0", "urllib3": "2.0.7",
               "jinja2": "3.1.2", "pyyaml": "6.0.2", "idna": "3.7"}
    for rivi in raportti(lukitus):
        print(rivi)
    print("versiovertailu numeroina: 2.10 > 2.9:",
          versio("2.10") > versio("2.9"), "| merkkijonoina:",
          "2.10" > "2.9")


if __name__ == "__main__":
    main()
