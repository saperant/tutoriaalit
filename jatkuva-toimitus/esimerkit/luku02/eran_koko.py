"""Erän koko ja vian paikantaminen.

Jokaisessa muutoksessa on pieni todennäköisyys rikkoa jotain. Mitä
useampi muutos integroidaan kerralla, sitä varmemmin erä on rikki ja
sitä useampi muutos on epäiltynä.
"""

from math import ceil, log2

VIKA = 0.02          # todennäköisyys, että yksittäinen muutos rikkoo rungon


# @alku era
def era_rikki(koko: int, vika: float = VIKA) -> float:
    """Todennäköisyys, että erässä on ainakin yksi rikkova muutos."""
    return 1 - (1 - vika) ** koko


def puolitusaskelia(koko: int) -> int:
    """Montako kertaa erä on puolitettava ja testattava syyn löytämiseksi."""
    return ceil(log2(koko)) if koko > 1 else 0
# @loppu era


print(f"{'erän koko':>10}{'erä rikki':>11}{'epäiltyjä':>11}"
      f"{'puolituksia':>13}")
for koko in (1, 5, 20, 50, 200):
    print(f"{koko:>10}{era_rikki(koko):>11.0%}{koko:>11}"
          f"{puolitusaskelia(koko):>13}")
