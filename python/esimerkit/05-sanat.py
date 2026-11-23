"""Tekstin yleisimmät sanat ja niiden osuudet."""

import re
import sys
from collections import Counter

# @alku sanat
SANA = re.compile(r"[a-zåäö]+")

teksti = sys.stdin.read().lower()
laskuri = Counter(SANA.findall(teksti))
yhteensa = laskuri.total()
for sana, maara in laskuri.most_common(4):
    print(f"{sana:<14}{maara:>3}{maara / yhteensa:>8.1%}")
print(f"eri sanoja {len(laskuri)}, sanoja yhteensä {yhteensa}")
# @loppu sanat
