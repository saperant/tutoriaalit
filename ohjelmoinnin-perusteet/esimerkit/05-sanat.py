"""Laskee tekstin yleisimmät sanat sanakirjan avulla."""

import sys

lukumaarat: dict[str, int] = {}
for rivi in sys.stdin:
    for sana in rivi.lower().split():
        sana = sana.strip(".,:;!?\"'()")
        if sana:
            lukumaarat[sana] = lukumaarat.get(sana, 0) + 1

print(f"Eri sanoja: {len(lukumaarat)}")
yleisimmat = sorted(lukumaarat.items(), key=lambda pari: pari[1],
                    reverse=True)
for sana, maara in yleisimmat[:4]:
    print(f"{sana:<10}{maara}")
print("Esiintyykö 'kissa'?", "kissa" in lukumaarat)
