"""Kiekko, saanto ja hinta: montako toimivaa piiriä saadaan?

Piirejä mahtuu kiekolle sitä vähemmän, mitä suurempi piiri on, ja
virheet osuvat suureen piiriin todennäköisemmin. Saanto arvioidaan
virhetiheydestä Poissonin ja Murphyn malleilla.
"""

import math

# @alku malli
KIEKKO_MM = 200.0          # kiekon halkaisija
KIEKON_HINTA = 3000.0      # € käsiteltynä (130 nm, havainnollinen)
VIRHETIHEYS = 0.25         # virhettä / cm²


def piireja_kiekolla(ala_mm2: float) -> int:
    """Yleinen arvio: kiekon ala jaettuna piirin alalla, miinus
    reunalle jäävät vajaat piirit."""
    d = KIEKKO_MM
    return int(math.pi * (d / 2) ** 2 / ala_mm2
               - math.pi * d / math.sqrt(2 * ala_mm2))


def saanto(ala_mm2: float) -> tuple[float, float]:
    """(Poisson, Murphy): todennäköisyys, ettei piirissä ole virhettä."""
    ad = ala_mm2 / 100 * VIRHETIHEYS
    poisson = math.exp(-ad)
    murphy = ((1 - math.exp(-ad)) / ad) ** 2
    return poisson, murphy
# @loppu malli


def main() -> None:
    # @alku taulukko
    print("ala mm²  piirejä  saanto P/M     toimivia   € / toimiva")
    for ala in [4, 25, 100, 400]:
        n = piireja_kiekolla(ala)
        p, m = saanto(ala)
        toimivia = n * m
        print(f"{ala:7} {n:8} {p:6.0%} / {m:4.0%} {toimivia:10.0f} "
              f"{KIEKON_HINTA / toimivia:12.2f}")
    # @loppu taulukko


if __name__ == "__main__":
    main()
