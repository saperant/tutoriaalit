"""Rahakkeen ämpäri (token bucket): nopeusrajoitus, joka sallii purskeet."""

from dataclasses import dataclass


# @alku ampari
@dataclass
class Ampari:
    nopeus: float          # rahaketta sekunnissa (tavua/s)
    koko: float            # ämpärin koko (tavua)
    rahakkeita: float = 0.0
    edellinen: float = 0.0

    def __post_init__(self) -> None:
        self.rahakkeita = self.koko

    def salli(self, aika: float, tavua: int) -> bool:
        kulunut = aika - self.edellinen
        self.edellinen = aika
        self.rahakkeita = min(self.koko,
                              self.rahakkeita + kulunut * self.nopeus)
        if tavua <= self.rahakkeita:
            self.rahakkeita -= tavua
            return True
        return False                 # pudotetaan tai merkitään
# @loppu ampari


# 1 Mbit/s = 125 000 tavua/s, purske enintään 10 pakettia.
ampari = Ampari(nopeus=125_000, koko=15_000)
# @alku liikenne
# Ensin 20 paketin purske, sitten tasainen virta 0,8 Mbit/s.
saapumiset = [(0.0001 * i, 1500) for i in range(20)]
saapumiset += [(0.1 + 0.015 * i, 1500) for i in range(20)]
hyvaksytyt = [ampari.salli(t, koko) for t, koko in saapumiset]
print("purske:  ", "".join("+" if h else "-" for h in hyvaksytyt[:20]))
print("tasainen:", "".join("+" if h else "-" for h in hyvaksytyt[20:]))
# @loppu liikenne
