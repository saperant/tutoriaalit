"""Ongelman ehtoluku: kuinka paljon syötteen pieni virhe kasvaa."""

import math
from collections.abc import Callable


# @alku ehtoluku
def ehtoluku(f: Callable[[float], float], df: Callable[[float], float],
             x: float) -> float:
    """Suhteellinen ehtoluku |x f'(x) / f(x)|."""
    return abs(x * df(x) / f(x))


def kokeile(nimi: str, f: Callable[[float], float],
            df: Callable[[float], float], x: float) -> None:
    hairio = 1e-10                         # syötteen suhteellinen virhe
    muutos = abs(f(x * (1 + hairio)) - f(x)) / abs(f(x))
    print(f"{nimi:18s} ehtoluku {ehtoluku(f, df, x):8.1e}   "
          f"havaittu vahvistus {muutos / hairio:8.1e}")


kokeile("sqrt(x), x=2", math.sqrt, lambda x: 0.5 / math.sqrt(x), 2.0)
kokeile("exp(x), x=30", math.exp, math.exp, 30.0)
kokeile("log(x), x=1.0001", math.log, lambda x: 1 / x, 1.0001)
kokeile("tan(x), x=1.5707", math.tan,
        lambda x: 1 / math.cos(x) ** 2, 1.5707)
# @loppu ehtoluku
