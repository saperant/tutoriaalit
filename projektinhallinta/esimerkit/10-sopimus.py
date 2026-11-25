"""Sopimusmalli jakaa riskin: kuka maksaa, kun työ venyy?

Työn todellinen kustannus toimittajalle on epävarma (mediaani 100 t€,
vino jakauma). Lasketaan asiakkaan maksu ja toimittajan kate kolmella
sopimusmallilla samoista toteumista.
"""

import random
import statistics

KATE = 0.15
rng = random.Random(17)
KUSTANNUKSET = sorted(100 * rng.lognormvariate(0, 0.35)
                      for _ in range(20_000))
ODOTUS = statistics.mean(KUSTANNUKSET)
P85 = KUSTANNUKSET[int(0.85 * len(KUSTANNUKSET))]


# @alku mallit
def tuntityo(kustannus: float) -> float:
    """Asiakas maksaa toteuman ja katteen sen päälle."""
    return kustannus * (1 + KATE)


def kiintea(kustannus: float) -> float:
    """Toimittaja hinnoittelee riskin: 85 %:n varmuus ja kate."""
    return P85 * (1 + KATE)


def tavoitehinta(kustannus: float) -> float:
    """Ylitys ja alitus jaetaan puoliksi tavoitekustannuksen ympärillä."""
    palkkio = ODOTUS * KATE
    return ODOTUS + palkkio + 0.5 * (kustannus - ODOTUS)
# @loppu mallit


def pers(arvot: list[float], osuus: float) -> float:
    return sorted(arvot)[int(osuus * len(arvot))]


print(f"kustannus toimittajalle: keskiarvo {ODOTUS:.0f}, 85 % {P85:.0f} t€")
print(f"{'malli':<14}{'asiakas ka.':>12}{'asiakas 95 %':>14}"
      f"{'kate ka.':>10}{'toimittaja tappiolla':>22}")
for nimi, malli in (("tuntityö", tuntityo), ("kiinteä hinta", kiintea),
                    ("tavoitehinta", tavoitehinta)):
    maksut = [malli(k) for k in KUSTANNUKSET]
    katteet = [m - k for m, k in zip(maksut, KUSTANNUKSET, strict=True)]
    tappiolla = sum(k < 0 for k in katteet) / len(katteet)
    print(f"{nimi:<14}{statistics.mean(maksut):>9.0f} t€"
          f"{pers(maksut, 0.95):>11.0f} t€"
          f"{statistics.mean(katteet):>7.0f} t€{tappiolla:>21.0%}")
