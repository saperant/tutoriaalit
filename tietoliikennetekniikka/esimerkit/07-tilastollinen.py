"""Piirikytkentä vai pakettikytkentä: tilastollinen multipleksointi."""

import math

import numpy as np

LINKKI = 100e6              # bit/s
KAYTTAJAN_NOPEUS = 10e6     # bit/s silloin kun käyttäjä lähettää
AKTIIVISUUS = 0.1           # käyttäjä lähettää 10 % ajasta

# @alku vertailu
# Piirikytkentä varaa jokaiselle käyttäjälle oman kaistansa koko ajaksi.
piireja = int(LINKKI // KAYTTAJAN_NOPEUS)
print(f"piirikytkentä: {piireja} käyttäjää")


# Pakettikytkentä jakaa kaistan tarpeen mukaan. Ruuhka syntyy vain, kun
# yli 10 käyttäjää on aktiivisena yhtä aikaa (binomijakauma).
def ruuhkan_todennakoisyys(kayttajia: int) -> float:
    return sum(math.comb(kayttajia, k) * AKTIIVISUUS ** k
               * (1 - AKTIIVISUUS) ** (kayttajia - k)
               for k in range(piireja + 1, kayttajia + 1))


for n in (20, 35, 50):
    print(f"pakettikytkentä, {n} käyttäjää: ruuhkaa"
          f" {ruuhkan_todennakoisyys(n):.4%} ajasta")
# @loppu vertailu

# @alku simulaatio
rng = np.random.default_rng(4)
aktiivisia = rng.binomial(35, AKTIIVISUUS, size=1_000_000)
print(f"simuloitu, 35 käyttäjää: ruuhkaa {np.mean(aktiivisia > 10):.4%}")
# @loppu simulaatio
