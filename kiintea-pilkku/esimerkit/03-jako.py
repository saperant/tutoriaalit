"""Jako vakiolla ilman jakajaa: kerrotaan käänteisluvun kiinteän pilkun
koodilla ja siirretään. Tyhjentävä tarkistus 16-bittisillä luvuilla."""


# @alku kaanteisluku
def kaanteisluku(jakaja: int, murtobitit: int) -> int:
    """1/jakaja muodossa UQ0.murtobitit ylöspäin pyöristettynä."""
    return -(-(1 << murtobitit) // jakaja)


def jaa_vakiolla(x: int, koodi: int, murtobitit: int) -> int:
    return (x * koodi) >> murtobitit      # laitteistossa kertoja ja johdotus
# @loppu kaanteisluku


# @alku tarkistus
# Etumerkitön 16-bittinen x jaettuna kymmenellä: montako murtobittiä
# käänteisluku tarvitsee, jotta tulos on sama kuin x // 10 kaikilla x?
for murtobitit in (16, 17, 18, 19):
    koodi = kaanteisluku(10, murtobitit)
    virheet = [x for x in range(1 << 16)
               if jaa_vakiolla(x, koodi, murtobitit) != x // 10]
    tila = "oikein kaikilla x" if not virheet else (
        f"{len(virheet)} väärää, ensimmäinen x = {virheet[0]}")
    print(f"1/10 = {koodi:#x} / 2^{murtobitit} "
          f"({koodi.bit_length()} bittiä): {tila}")
# @loppu tarkistus

# @alku skaalaus
# Skaalaus murtoluvulla: Q1.15-näyte kerrotaan vakiolla 1/3. Koodi
# pyöristetään lähimpään, ja virhe on enintään puoli koodin LSB:tä.
koodi = round((1 << 15) / 3)
print(f"1/3 = {koodi} / 2^15 = {koodi / (1 << 15):.6f}, "
      f"suhteellinen virhe {abs(koodi / (1 << 15) * 3 - 1):.1e}")
# @loppu skaalaus
