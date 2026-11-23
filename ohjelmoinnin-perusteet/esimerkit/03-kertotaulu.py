"""Tulostaa kertotaulun sisäkkäisillä silmukoilla."""

KOKO = 5
for rivi in range(1, KOKO + 1):
    for sarake in range(1, KOKO + 1):
        print(f"{rivi * sarake:4}", end="")
    print()   # rivinvaihto rivin loppuun
