"""Naiivi Bayes -roskapostisuodatin pienellä opetusaineistolla."""

import math
from collections import Counter

# @alku aineisto
OPETUS = [
    ("roska", "voita ilmainen matka nyt klikkaa"),
    ("roska", "ilmainen tarjous vain tänään klikkaa linkkiä"),
    ("roska", "olet voittanut rahaa lähetä tilinumero"),
    ("roska", "halpa laina heti ilman takaajaa"),
    ("hyvä", "palaveri siirtyy huomiseen kello kymmenen"),
    ("hyvä", "liitteenä viikon raportti ja tarjous asiakkaalle"),
    ("hyvä", "muista koodikatselmointi ennen julkaisua"),
    ("hyvä", "lounas tänään kello yksitoista"),
]
# @loppu aineisto


# @alku malli
def opeta(aineisto: list[tuple[str, str]]) -> tuple[
        dict[str, Counter[str]], Counter[str], set[str]]:
    sanat: dict[str, Counter[str]] = {"roska": Counter(), "hyvä": Counter()}
    luokat: Counter[str] = Counter()
    for luokka, teksti in aineisto:
        luokat[luokka] += 1
        sanat[luokka].update(teksti.split())
    sanasto = set().union(*(set(c) for c in sanat.values()))
    return sanat, luokat, sanasto


def log_uskottavuus(teksti: str, luokka: str,
                    malli: tuple[dict[str, Counter[str]], Counter[str],
                                 set[str]]) -> float:
    """log P(luokka) + summa log P(sana | luokka), Laplace-tasoitus."""
    sanat, luokat, sanasto = malli
    tulos = math.log(luokat[luokka] / sum(luokat.values()))
    yhteensa = sum(sanat[luokka].values())
    for sana in teksti.split():
        lkm = sanat[luokka][sana] + 1          # +1: tuntematon sana ei
        tulos += math.log(lkm / (yhteensa + len(sanasto)))  # nollaa
    return tulos
# @loppu malli


# @alku luokittelu
malli = opeta(OPETUS)
for viesti in ("ilmainen laina klikkaa", "raportti palaveri huomenna",
               "tarjous asiakkaalle tänään"):
    roska = log_uskottavuus(viesti, "roska", malli)
    hyva = log_uskottavuus(viesti, "hyvä", malli)
    # Posteriori log-arvoista: 1 / (1 + exp(hyvä - roska)).
    p = 1 / (1 + math.exp(hyva - roska))
    print(f"{viesti:30} P(roska) = {p:.2f}")
# @loppu luokittelu
