"""Huippunopeuden laskeminen (3GPP TS 38.306, kaava 4.1.2)."""

# @alku kaava
def huippunopeus_mbit(kerroksia: int, bittia_symbolissa: int,
                      lohkoja: int, mu: int, ylimaarainen: float,
                      koodisuhde: float = 948 / 1024) -> float:
    symboliaika = 1e-3 / (14 * 2 ** mu)
    return float(1e-6 * kerroksia * bittia_symbolissa * koodisuhde
                 * lohkoja * 12 / symboliaika * (1 - ylimaarainen))
# @loppu kaava


# @alku esimerkit
# 5G NR, 100 MHz, 30 kHz, 4 MIMO-kerrosta, 256-QAM, alalinkki.
nr = huippunopeus_mbit(4, 8, 273, mu=1, ylimaarainen=0.14)
# Sama mutta 2 kerrosta ja 64-QAM: tyypillisempi päätelaite.
nr_tavallinen = huippunopeus_mbit(2, 6, 273, mu=1, ylimaarainen=0.14)
# LTE-tyyppinen 20 MHz, 15 kHz, 2 kerrosta, 64-QAM.
lte = huippunopeus_mbit(2, 6, 100, mu=0, ylimaarainen=0.25)
print(f"NR 100 MHz, 4×256-QAM: {nr:7.0f} Mbit/s")
print(f"NR 100 MHz, 2×64-QAM:  {nr_tavallinen:7.0f} Mbit/s")
print(f"LTE 20 MHz, 2×64-QAM:  {lte:7.0f} Mbit/s")
# Huippunopeus jaetaan solun kaikkien käyttäjien kesken.
print(f"NR-solu 40 aktiivisella: {nr / 40:5.1f} Mbit/s käyttäjää kohti")
# @loppu esimerkit
