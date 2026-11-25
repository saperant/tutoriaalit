"""Tiimitopologia datana ja nyrkkisäännöt, jotka sen voi tarkistaa."""

from dataclasses import dataclass

# @alku topologia
TIIMIT = {
    "hakutiimi": "virta", "ostotiimi": "virta", "tilaustiimi": "virta",
    "maksutiimi": "virta", "alustatiimi": "alusta",
    "testaustuki": "mahdollistava", "hinnoittelulaskenta": "osajärjestelmä",
}


@dataclass(frozen=True)
class Vuorovaikutus:
    a: str
    b: str
    tapa: str          # yhteistyö, palveluna tai fasilitointi
    viikkoja: int      # kuinka kauan jatkunut; 0 = pysyvä palvelusuhde


VUOROVAIKUTUKSET = [
    Vuorovaikutus("hakutiimi", "alustatiimi", "palveluna", 0),
    Vuorovaikutus("ostotiimi", "alustatiimi", "palveluna", 0),
    Vuorovaikutus("ostotiimi", "hinnoittelulaskenta", "palveluna", 0),
    Vuorovaikutus("tilaustiimi", "alustatiimi", "yhteistyö", 6),
    Vuorovaikutus("tilaustiimi", "maksutiimi", "yhteistyö", 40),
    Vuorovaikutus("maksutiimi", "alustatiimi", "yhteistyö", 30),
    Vuorovaikutus("testaustuki", "hakutiimi", "fasilitointi", 8),
    Vuorovaikutus("testaustuki", "ostotiimi", "fasilitointi", 52),
]
# @loppu topologia

YHTEISTYON_RAJA = 12       # viikkoa
FASILITOINNIN_RAJA = 26


# @alku saannot
def havainnot() -> list[str]:
    tulos = []
    virtatiimeja = sum(tyyppi == "virta" for tyyppi in TIIMIT.values())
    if virtatiimeja * 2 < len(TIIMIT):
        tulos.append("alle puolet tiimeistä on virtaan linjattuja")
    for v in VUOROVAIKUTUKSET:
        pari = f"{v.a} - {v.b}"
        if v.tapa == "yhteistyö" and v.viikkoja > YHTEISTYON_RAJA:
            tulos.append(f"{pari}: yhteistyö jatkunut {v.viikkoja} vk, "
                         "sovi rajapinta")
        if v.tapa == "fasilitointi" and v.viikkoja > FASILITOINNIN_RAJA:
            tulos.append(f"{pari}: fasilitointi jatkunut {v.viikkoja} vk, "
                         "osaaminen ei siirry")
    for tiimi in TIIMIT:
        yhteistyot = [v for v in VUOROVAIKUTUKSET if v.tapa == "yhteistyö"
                      and tiimi in (v.a, v.b)]
        if len(yhteistyot) > 1:
            tulos.append(f"{tiimi}: {len(yhteistyot)} yhteistyösuhdetta "
                         "yhtä aikaa")
    return tulos
# @loppu saannot


virta = sum(tyyppi == "virta" for tyyppi in TIIMIT.values())
print(f"tiimejä {len(TIIMIT)}, joista virtaan linjattuja {virta}")
for havainto in havainnot():
    print(f"- {havainto}")
