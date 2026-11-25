"""Milloin 60 työtä on valmiina, ja paljonko ehtii 12 viikossa?"""

import math

from ennuste import HISTORIA, maaraennuste, persentiili, valmistumisennuste

TOITA, VIIKKOJA = 60, 12

keskiarvo = sum(HISTORIA) / len(HISTORIA)
print(f"keskiläpäisy {keskiarvo:.2f} työtä/vk -> "
      f"{TOITA}/{keskiarvo:.2f} = {math.ceil(TOITA / keskiarvo)} viikkoa")

# @alku milloin
viikot = valmistumisennuste(HISTORIA, TOITA)
print(f"milloin {TOITA} työtä on valmiina?")
for varmuus in (0.50, 0.85, 0.95):
    print(f"  {varmuus:4.0%}:n varmuudella viimeistään viikolla "
          f"{persentiili(viikot, varmuus)}")
keskiarvolla = math.ceil(TOITA / keskiarvo)
osuus = sum(v <= keskiarvolla for v in viikot) / len(viikot)
print(f"  keskiarvoon perustuva lupaus pitää {osuus:.0%} tapauksista")
# @loppu milloin

# @alku paljonko
maarat = maaraennuste(HISTORIA, VIIKKOJA)
print(f"montako työtä valmistuu {VIIKKOJA} viikossa?")
for varmuus in (0.50, 0.85, 0.95):
    # Varma lupaus on jakauman alapäästä: vähintään näin monta.
    print(f"  {varmuus:4.0%}:n varmuudella vähintään "
          f"{persentiili(maarat, 1 - varmuus)}")
# @loppu paljonko
