"""Päivitystilanne palvelinkannasta: mitkä koneet vaativat toimia.

Inventaario kerätään koneilta (esim. Ansiblen facts-tiedoista tai
valvontajärjestelmästä). Asennettu ydin ei ole käytössä ennen
uudelleenkäynnistystä, joten pelkkä päivittäminen ei riitä.
"""

import json
from datetime import date

INVENTAARIO = """[
 {"nimi": "web1", "ydin_kaytossa": "6.8.0-88", "ydin_asennettu": "6.8.0-88",
  "tietoturvapaivityksia": 0, "viimeksi_paivitetty": "2026-11-20"},
 {"nimi": "web2", "ydin_kaytossa": "6.8.0-79", "ydin_asennettu": "6.8.0-88",
  "tietoturvapaivityksia": 0, "viimeksi_paivitetty": "2026-11-20"},
 {"nimi": "db1", "ydin_kaytossa": "6.8.0-88", "ydin_asennettu": "6.8.0-88",
  "tietoturvapaivityksia": 7, "viimeksi_paivitetty": "2026-09-02"},
 {"nimi": "vanha-ftp", "ydin_kaytossa": "5.4.0-200",
  "ydin_asennettu": "5.4.0-200", "tietoturvapaivityksia": 31,
  "viimeksi_paivitetty": "2025-04-11", "tuki_paattyy": "2025-05-31"}
]"""


def versio(ydin: str) -> tuple[int, ...]:
    return tuple(int(osa) for osa in ydin.replace("-", ".").split("."))


# @alku tilanne
def toimenpiteet(kone: dict[str, object], tanaan: date) -> list[str]:
    tehtavat = []
    if versio(str(kone["ydin_asennettu"])) > versio(
            str(kone["ydin_kaytossa"])):
        tehtavat.append("käynnistä uudelleen (uusi ydin odottaa)")
    if int(str(kone["tietoturvapaivityksia"])) > 0:
        tehtavat.append(f"asenna {kone['tietoturvapaivityksia']} "
                        "tietoturvapäivitystä")
    ika = (tanaan - date.fromisoformat(str(kone["viimeksi_paivitetty"])))
    if ika.days > 30:
        tehtavat.append(f"päivitetty {ika.days} päivää sitten")
    tuki = kone.get("tuki_paattyy")
    if tuki and date.fromisoformat(str(tuki)) < tanaan:
        tehtavat.append("käyttöjärjestelmän tuki päättynyt: korvaa")
    return tehtavat
# @loppu tilanne


def main() -> None:
    tanaan = date(2026, 11, 24)
    for kone in json.loads(INVENTAARIO):
        tehtavat = toimenpiteet(kone, tanaan)
        print(f"{kone['nimi']:10} ok" if not tehtavat else kone["nimi"])
        for t in tehtavat:
            print(f"  - {t}")


if __name__ == "__main__":
    main()
