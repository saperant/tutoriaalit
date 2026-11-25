"""Luovutusten hinta: erikoistiimien ketju vastaan ominaisuustiimit.

Sama työ ja sama väkimäärä (12 henkeä) kahdella tavalla järjestettynä.
Jokaisessa työssä on kolme vaihetta: käyttöliittymä, rajapinta ja
tietokanta.
"""

import heapq
import math
import random
import statistics

TOITA = 6000
SAAPUMISIA_PAIVASSA = 3.2      # kuormitusaste 80 % molemmissa malleissa
VIRTOJA = 4


# @alku jono
def jono(saapumiset: list[float], kestot: list[float],
         tekijoita: int) -> list[float]:
    """Saapumisjärjestyksessä palveleva jono: töiden valmistumisajat."""
    vapautuu = [0.0] * tekijoita
    valmiit = [0.0] * len(saapumiset)
    for i in sorted(range(len(saapumiset)), key=saapumiset.__getitem__):
        alku = max(saapumiset[i], heapq.heappop(vapautuu))
        valmiit[i] = alku + kestot[i]
        heapq.heappush(vapautuu, valmiit[i])
    return valmiit
# @loppu jono


# @alku mallit
def erikoistiimit(saapumiset: list[float], vaiheet: list[list[float]],
                  ottovali: float) -> list[float]:
    """Kolme neljän hengen tiimiä peräkkäin. Seuraava tiimi ottaa työn
    jonoonsa vasta seuraavassa työjonon läpikäynnissä (ottovali päivää)."""
    hetket = saapumiset
    for vaihe in range(3):
        if vaihe > 0 and ottovali > 0:
            hetket = [math.ceil(h / ottovali) * ottovali for h in hetket]
        hetket = jono(hetket, [v[vaihe] for v in vaiheet], tekijoita=4)
    return hetket


def ominaisuustiimit(saapumiset: list[float], vaiheet: list[list[float]],
                     virrat: list[int], hidastus: float) -> list[float]:
    """Neljä kolmen hengen tiimiä; tekijä vie työn alusta loppuun.
    Hidastus kuvaa sitä, että yleisosaaja on erikoisosaajaa hitaampi."""
    valmiit = [0.0] * len(saapumiset)
    for virta in range(VIRTOJA):
        omat = [i for i, v in enumerate(virrat) if v == virta]
        tulos = jono([saapumiset[i] for i in omat],
                     [sum(vaiheet[i]) * hidastus for i in omat], 3)
        for i, valmis in zip(omat, tulos, strict=True):
            valmiit[i] = valmis
    return valmiit
# @loppu mallit


def tyot(siemen: int = 3) -> tuple[list[float], list[list[float]],
                                   list[int]]:
    """Samat työt molemmille malleille: saapumisajat, vaiheiden kestot
    (keskimäärin päivä vaihetta kohden) ja virta, johon työ kuuluu."""
    rng = random.Random(siemen)
    hetki = 0.0
    saapumiset, vaiheet, virrat = [], [], []
    for _ in range(TOITA):
        hetki += rng.expovariate(SAAPUMISIA_PAIVASSA)
        saapumiset.append(hetki)
        vaiheet.append([rng.expovariate(1.0) for _ in range(3)])
        virrat.append(rng.randrange(VIRTOJA))
    return saapumiset, vaiheet, virrat


def tunnusluvut(saapumiset: list[float], valmiit: list[float],
                tyoaika: float) -> tuple[float, float, float]:
    """Läpimenoajan keskiarvo ja 85. prosenttipiste sekä virtaustehokkuus
    eli työajan osuus läpimenoajasta."""
    ajat = sorted(v - s for s, v in zip(saapumiset, valmiit, strict=True))
    keski = statistics.fmean(ajat)
    return keski, ajat[int(0.85 * len(ajat))], tyoaika / keski


if __name__ == "__main__":
    saapumiset, vaiheet, virrat = tyot()
    tyoaika = statistics.fmean(sum(v) for v in vaiheet)
    print(f"{'malli':38}{'keskim.':>8}{'85 %':>7}{'tehokkuus':>11}")
    for ottovali, kuvaus in ((0, "työ siirtyy heti"),
                             (1, "läpikäynti päivittäin"),
                             (5, "läpikäynti viikoittain")):
        valmiit = erikoistiimit(saapumiset, vaiheet, ottovali)
        k, p85, teho = tunnusluvut(saapumiset, valmiit, tyoaika)
        print(f"{'erikoistiimit, ' + kuvaus:38}{k:8.1f}{p85:7.1f}"
              f"{teho:10.0%}")
    for hidastus in (1.0, 1.15):
        valmiit = ominaisuustiimit(saapumiset, vaiheet, virrat, hidastus)
        k, p85, teho = tunnusluvut(saapumiset, valmiit, tyoaika * hidastus)
        nimi = f"ominaisuustiimit, hidastus {hidastus:.2f}"
        print(f"{nimi:38}{k:8.1f}{p85:7.1f}{teho:10.0%}")
