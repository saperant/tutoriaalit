"""Pinta-alasta hinnaksi: piirin hinta kasvaa pinta-alaa nopeammin,
koska suureen piiriin osuu virhe todennäköisemmin (Hennessy ja
Patterson, luku 1)."""

import math

# @alku malli
KIEKKO_MM = 300.0  # kiekon halkaisija
KIEKON_HINTA = 10_000.0  # € käsiteltynä (havainnollinen)
VIRHETIHEYS = 0.1  # virhettä / cm²


def piireja_kiekolla(ala_mm2: float) -> float:
    """Kiekon ala jaettuna piirin alalla, miinus reunan vajaat piirit."""
    d = KIEKKO_MM
    return (math.pi * (d / 2) ** 2 / ala_mm2
            - math.pi * d / math.sqrt(2 * ala_mm2))


def saanto(ala_mm2: float) -> float:
    """Murphyn malli: toimivien osuus, kun virheet osuvat satunnaisesti."""
    ad = ala_mm2 / 100 * VIRHETIHEYS
    return ((1 - math.exp(-ad)) / ad) ** 2


def hinta(ala_mm2: float) -> float:
    """Yhden toimivan piirin hinta (€)."""
    return KIEKON_HINTA / (piireja_kiekolla(ala_mm2) * saanto(ala_mm2))
# @loppu malli


def main() -> None:
    # @alku taulukko
    print(f"{'mm2':>5} {'piirejä':>8} {'saanto':>7} {'€/piiri':>8}"
          f" {'€/mm2':>6}")
    for ala in (50, 100, 200, 400, 800):
        print(f"{ala:>5} {piireja_kiekolla(ala):8.0f} {saanto(ala):7.0%}"
              f" {hinta(ala):8.2f} {hinta(ala) / ala:6.3f}")
    # @loppu taulukko
    # @alku jako
    # Sama logiikka yhtenä 800 mm2:n piirinä vai neljänä 200 mm2:n
    # palana, jotka testataan erikseen ja kootaan yhteen koteloon.
    yksi, nelja = hinta(800), 4 * hinta(200)
    print(f"\nyksi 800 mm2: {yksi:.0f} €, neljä 200 mm2: {nelja:.0f} €"
          f" ({nelja / yksi:.0%})")
    # @loppu jako


if __name__ == "__main__":
    main()
