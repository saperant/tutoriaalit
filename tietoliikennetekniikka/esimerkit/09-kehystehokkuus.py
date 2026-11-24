"""Ethernet-kehyksen yleiskustannus ja kehysnopeus."""

# @alku kehys
ALKUTAHDISTE = 7 + 1     # preamble + SFD
OTSAKE = 6 + 6 + 2       # kohde, lähde, EtherType
FCS = 4                  # CRC-32
KEHYSVALI = 12           # inter-frame gap tavuina
YLIMAARAINEN = ALKUTAHDISTE + OTSAKE + FCS + KEHYSVALI


def tehokkuus(hyotykuorma: int) -> float:
    return hyotykuorma / (hyotykuorma + YLIMAARAINEN)


def kehyksia_sekunnissa(hyotykuorma: int, linja_bit_s: float) -> float:
    return linja_bit_s / ((hyotykuorma + YLIMAARAINEN) * 8)
# @loppu kehys


print(f"yleiskustannus {YLIMAARAINEN} tavua kehystä kohti")
print("hyötykuorma  tehokkuus  kehystä/s @ 10 Gbit/s")
for kuorma in (46, 512, 1500, 9000):
    print(f"{kuorma:>11}  {tehokkuus(kuorma):>9.1%}"
          f"  {kehyksia_sekunnissa(kuorma, 10e9) / 1e6:>8.3f} milj.")
