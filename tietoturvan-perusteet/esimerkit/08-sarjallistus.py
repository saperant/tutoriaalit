"""Turvaton deserialisointi: pickle suorittaa koodia ladattaessa."""

import json
import pickle
from dataclasses import dataclass


# @alku hyokkays
class Hyotykuorma:
    """Hyökkääjän olio: __reduce__ kertoo picklelle, mitä kutsutaan,
    kun olio ladataan. Oikea hyökkäys kutsuisi esim. os.system."""

    def __reduce__(self) -> tuple[object, tuple[str]]:
        return print, ("hyökkääjän koodi suoritettiin latauksessa",)


evaste = pickle.dumps(Hyotykuorma())   # esim. evästeessä selaimelta
pickle.loads(evaste)  # noqa: S301 – juuri tämä on haavoittuvuus
# @loppu hyokkays


# @alku korjattu
@dataclass(frozen=True)
class Ostoskori:
    tuotteet: tuple[str, ...]


def lataa(data: str) -> Ostoskori:
    """JSON on pelkkää dataa; rakenne tarkistetaan ennen käyttöä."""
    arvo = json.loads(data)
    if not isinstance(arvo, dict) or set(arvo) != {"tuotteet"}:
        raise ValueError("väärä rakenne")
    tuotteet = arvo["tuotteet"]
    if not (isinstance(tuotteet, list)
            and all(isinstance(t, str) for t in tuotteet)):
        raise ValueError("tuotteet: lista merkkijonoja")
    return Ostoskori(tuple(tuotteet))
# @loppu korjattu


print(lataa('{"tuotteet": ["kahvi", "maito"]}'))
for huono in ['{"__class__": "os.system"}', '{"tuotteet": [1, 2]}']:
    try:
        lataa(huono)
    except ValueError as virhe:
        print("hylätty:", virhe)
