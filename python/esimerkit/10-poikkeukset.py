"""Oma poikkeushierarkia, ketjutus ja siivous."""

import json


# @alku hierarkia
class SovellusVirhe(Exception):
    """Kaikkien tämän sovelluksen virheiden kantaluokka."""


class KonfiguraatioVirhe(SovellusVirhe):
    def __init__(self, avain: str, syy: str) -> None:
        super().__init__(f"{avain}: {syy}")
        self.avain = avain
# @loppu hierarkia


# @alku ketjutus
def lue_portti(teksti: str) -> int:
    try:
        asetukset = json.loads(teksti)
        portti = int(asetukset["portti"])
    except KeyError:
        raise KonfiguraatioVirhe("portti", "puuttuu") from None
    except (ValueError, TypeError) as virhe:
        raise KonfiguraatioVirhe("portti", "ei kokonaisluku") from virhe
    if not 1 <= portti <= 65535:
        raise KonfiguraatioVirhe("portti", f"alueen ulkopuolella: {portti}")
    return portti
# @loppu ketjutus


# @alku kaytto
for syote in ['{"portti": 8080}', "{}", '{"portti": "http"}',
              '{"portti": 70000}', "rikki"]:
    try:
        print("portti", lue_portti(syote))
    except SovellusVirhe as virhe:
        syy = type(virhe.__cause__).__name__ if virhe.__cause__ else "-"
        print(f"virhe: {virhe} (alkuperäinen: {syy})")
# @loppu kaytto
