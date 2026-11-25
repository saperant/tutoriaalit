"""Priorisointi viivästymisen hinnalla (WSJF) ja sen herkkyys arvioille.

Yksi tiimi tekee työt peräkkäin. Jokainen työ maksaa viivästymisen
hintansa verran jokaiselta viikolta, jonka se odottaa valmistumistaan.
"""

import itertools
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Tyo:
    nimi: str
    hinta: float    # viivästymisen hinta, tuhatta euroa viikossa
    kesto: float    # viikkoa


TYOT = [
    Tyo("laskutus", 8, 4), Tyo("haku", 4, 1), Tyo("raportit", 4, 6),
    Tyo("kirjautuminen", 6, 2), Tyo("vienti", 1, 1), Tyo("mobiili", 9, 8),
]


# @alku hinta
def viiveen_hinta(jarjestys: Sequence[Tyo]) -> float:
    """Kokonaishinta: jokainen työ maksaa valmistumishetkeensä asti."""
    aika = summa = 0.0
    for tyo in jarjestys:
        aika += tyo.kesto
        summa += tyo.hinta * aika
    return summa


SAANNOT: dict[str, Callable[[Tyo], float]] = {
    "arvokkain ensin": lambda t: -t.hinta,
    "lyhin ensin": lambda t: t.kesto,
    "WSJF (hinta/kesto)": lambda t: -t.hinta / t.kesto,
}
# @loppu hinta

print(f"{'sääntö':<26}viiveen hinta (t€)")
print(f"{'saapumisjärjestys':<26}{viiveen_hinta(TYOT):6.0f}")
for nimi, avain in SAANNOT.items():
    print(f"{nimi:<26}{viiveen_hinta(sorted(TYOT, key=avain)):6.0f}")
paras = min(itertools.permutations(TYOT), key=viiveen_hinta)
print(f"{'paras 720 järjestyksestä':<26}{viiveen_hinta(paras):6.0f}")
wsjf_jarjestys = sorted(TYOT, key=SAANNOT["WSJF (hinta/kesto)"])
print("WSJF:", " > ".join(t.nimi for t in wsjf_jarjestys))


# @alku herkkyys
def kohinainen(tyo: Tyo, rng: random.Random, virhe: float) -> Tyo:
    """Arvio, jossa hinta ja kesto ovat kertoimen 1/(1+v)...(1+v) päässä."""
    def kerroin() -> float:
        return float((1 + virhe) ** rng.uniform(-1, 1))
    return Tyo(tyo.nimi, tyo.hinta * kerroin(), tyo.kesto * kerroin())


def keskihavio(virhe: float, toistoja: int = 4000) -> tuple[float, float]:
    """Paljonko arviovirhe maksaa ja kuinka usein kärki pysyy samana."""
    rng = random.Random(7)
    oikea = {t.nimi: t for t in TYOT}
    wsjf = SAANNOT["WSJF (hinta/kesto)"]
    optimi = viiveen_hinta(sorted(TYOT, key=wsjf))
    havio, sama_karki = 0.0, 0
    for _ in range(toistoja):
        arviot = sorted((kohinainen(t, rng, virhe) for t in TYOT), key=wsjf)
        toteuma = [oikea[t.nimi] for t in arviot]
        havio += viiveen_hinta(toteuma) / optimi - 1
        sama_karki += toteuma[0].nimi == "haku"
    return havio / toistoja, sama_karki / toistoja
# @loppu herkkyys


print()
print("arvioiden virhe   lisähinta   kärki oikein")
for virhe in (0.25, 0.5, 1.0, 2.0):
    havio, karki = keskihavio(virhe)
    print(f"kerroin {1 + virhe:4.2f}      {havio:6.1%}      {karki:5.0%}")
