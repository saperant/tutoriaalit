"""Päätöksen odotusaika: kokoontuva ryhmä vastaan neuvonantoprosessi."""

import random
import statistics

TYOPAIVIA = 250
PAATOKSIA_PAIVASSA = 0.6       # keskimäärin kolme viikossa


def saapumiset(siemen: int = 5) -> list[float]:
    rng = random.Random(siemen)
    hetki = 0.0
    tulos: list[float] = []
    while True:
        hetki += rng.expovariate(PAATOKSIA_PAIVASSA)
        if hetki >= TYOPAIVIA:
            return tulos
        tulos.append(hetki)


# @alku ryhma
def ryhma(asiat: list[float], vali: int, kapasiteetti: int) -> list[float]:
    """Ryhmä kokoontuu vali päivän välein ja ehtii käsitellä enintään
    kapasiteetti asiaa. Palauttaa käsiteltyjen asioiden odotusajat."""
    jono: list[float] = []
    odotukset = []
    seuraava = 0
    for kokous in range(vali, TYOPAIVIA * 3, vali):
        while seuraava < len(asiat) and asiat[seuraava] <= kokous:
            jono.append(asiat[seuraava])
            seuraava += 1
        for saapui in jono[:kapasiteetti]:
            odotukset.append(kokous - saapui)
        jono = jono[kapasiteetti:]
        if seuraava == len(asiat) and not jono:
            break
    return odotukset
# @loppu ryhma


def rivi(nimi: str, odotukset: list[float]) -> None:
    print(f"{nimi:34}{statistics.fmean(odotukset):>8.1f}"
          f"{max(odotukset):>9.1f}")


asiat = saapumiset()
print(f"päätöksiä vuodessa {len(asiat)}")
print(f"{'malli':34}{'keskim.':>8}{'pisin':>9}")
rivi("ryhmä 2 vk välein, 5 asiaa", ryhma(asiat, 10, 5))
rivi("ryhmä 2 vk välein, 8 asiaa", ryhma(asiat, 10, 8))
rivi("ryhmä viikoittain, 4 asiaa", ryhma(asiat, 5, 4))
# Neuvonantoprosessi: tekijä pyytää neuvot ja päättää itse, kun
# kommentointiaika (3 työpäivää) on kulunut. Jonoa ei synny.
rivi("neuvonantoprosessi, 3 pv", [3.0] * len(asiat))
