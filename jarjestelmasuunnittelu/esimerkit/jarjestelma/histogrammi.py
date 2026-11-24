"""Latenssihistogrammi Prometheuksen tapaan.

Histogrammi tallentaa vain lokeroiden laskurit, joten sen voi koota
monelta palvelimelta laskemalla laskurit yhteen. Persentiilit
arvioidaan koostetusta histogrammista. Valmiita persentiilejä ei voi
koota: kahden palvelimen p99-lukujen keskiarvo ei ole yhteinen p99.
"""

from __future__ import annotations

import bisect
import math
from collections.abc import Sequence


class Histogrammi:
    def __init__(self, rajat: Sequence[float]) -> None:
        if list(rajat) != sorted(set(rajat)):
            raise ValueError("lokeroiden rajojen on oltava kasvavat")
        self.rajat = list(rajat)
        self.laskurit = [0] * (len(self.rajat) + 1)   # viimeinen: +Inf
        self.summa = 0.0

    def havainto(self, arvo: float) -> None:
        self.laskurit[bisect.bisect_left(self.rajat, arvo)] += 1
        self.summa += arvo

    @property
    def maara(self) -> int:
        return sum(self.laskurit)

    def yhdista(self, muu: Histogrammi) -> Histogrammi:
        if muu.rajat != self.rajat:
            raise ValueError("vain samoin lokeroituja voi yhdistää")
        tulos = Histogrammi(self.rajat)
        tulos.laskurit = [a + b for a, b in zip(self.laskurit, muu.laskurit,
                                                strict=True)]
        tulos.summa = self.summa + muu.summa
        return tulos

    # @alku kvantiili
    def kvantiili(self, q: float) -> float:
        """Kuten PromQL:n histogram_quantile: etsitään lokero, jossa
        kertymä ylittää q·n, ja interpoloidaan lineaarisesti sen sisällä.
        Tarkkuus riippuu siis lokeroinnista."""
        if not 0 <= q <= 1 or self.maara == 0:
            return math.nan
        tavoite = q * self.maara
        kertyma = 0
        for i, n in enumerate(self.laskurit):
            if kertyma + n >= tavoite and n > 0:
                if i == len(self.rajat):
                    return self.rajat[-1]   # +Inf-lokero: yläraja tuntematon
                ala = self.rajat[i - 1] if i > 0 else 0.0
                return ala + (self.rajat[i] - ala) * (tavoite - kertyma) / n
            kertyma += n
        return self.rajat[-1]
    # @loppu kvantiili

    # @alku prometheus
    def prometheus(self, nimi: str, nimiot: str = "") -> list[str]:
        """Prometheuksen tekstimuoto: kertyvät _bucket-rivit, _sum ja
        _count. Nimiöt muodossa 'reitti="/x"'."""
        erotin = "," if nimiot else ""
        rivit, kertyma = [], 0
        for raja, n in zip([*self.rajat, math.inf], self.laskurit,
                           strict=True):
            kertyma += n
            le = "+Inf" if math.isinf(raja) else f"{raja:g}"
            rivit.append(f'{nimi}_bucket{{{nimiot}{erotin}le="{le}"}} '
                         f"{kertyma}")
        nimioilla = f"{{{nimiot}}}" if nimiot else ""
        rivit.append(f"{nimi}_sum{nimioilla} {self.summa:.6f}")
        rivit.append(f"{nimi}_count{nimioilla} {kertyma}")
        return rivit
    # @loppu prometheus


def tarkka_kvantiili(arvot: Sequence[float], q: float) -> float:
    """Persentiili raakadatasta (lähin järjestysluku -menetelmä)."""
    jarjestetty = sorted(arvot)
    i = max(0, math.ceil(q * len(jarjestetty)) - 1)
    return jarjestetty[i]
