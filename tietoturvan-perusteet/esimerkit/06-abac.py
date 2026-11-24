"""Attribuuttipohjainen pääsynhallinta (ABAC): sääntö ominaisuuksista."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Kayttaja:
    nimi: str
    osasto: str
    selvitystaso: int      # 0 julkinen, 1 sisäinen, 2 luottamuksellinen


@dataclass(frozen=True)
class Asiakirja:
    nimi: str
    osasto: str
    luokitus: int
    omistaja: str


# @alku abac
def saa_lukea(k: Kayttaja, a: Asiakirja, verkko: str) -> tuple[bool, str]:
    if a.omistaja == k.nimi:
        return True, "omistaja"
    if k.selvitystaso < a.luokitus:
        return False, "selvitystaso ei riitä"
    if a.luokitus >= 2 and verkko != "sisäverkko":
        return False, "luottamuksellinen vain sisäverkosta"
    if a.luokitus >= 1 and k.osasto != a.osasto:
        return False, "eri osasto"
    return True, "säännöt täyttyvät"
# @loppu abac


aino = Kayttaja("aino", "talous", 2)
pekka = Kayttaja("pekka", "varasto", 1)
budjetti = Asiakirja("budjetti 2027", "talous", 2, "liisa")
inventaario = Asiakirja("inventaario", "varasto", 1, "pekka")
for k, a, verkko in [(aino, budjetti, "sisäverkko"),
                     (aino, budjetti, "kotiverkko"),
                     (pekka, budjetti, "sisäverkko"),
                     (aino, inventaario, "sisäverkko"),
                     (pekka, inventaario, "kotiverkko")]:
    tulos, syy = saa_lukea(k, a, verkko)
    print(f"{k.nimi:<6} {a.nimi:<14} {verkko:<11} {tulos!s:<5} {syy}")
