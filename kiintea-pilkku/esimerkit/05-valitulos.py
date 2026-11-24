"""Kahden komplementin kierto antaa oikean summan, vaikka välitulos
ylittää alueen. Saturaatio välituloksissa rikkoo tämän."""

BITIT = 16
YLARAJA = (1 << (BITIT - 1)) - 1
ALARAJA = -(1 << (BITIT - 1))
SKAALA = 1 << (BITIT - 1)


# @alku summat
def kierra(x: int) -> int:
    """n-bittinen kiertävä tulos (alimmat bitit etumerkillisinä)."""
    return (x - ALARAJA) % (1 << BITIT) + ALARAJA


def saturoi(x: int) -> int:
    return max(ALARAJA, min(YLARAJA, x))


def q15(x: float) -> int:
    return round(x * SKAALA)


luvut = [q15(0.9), q15(0.7), q15(-0.8)]   # summa 0,8 mahtuu
kierto = saturaatio = 0
for luku in luvut:
    kierto = kierra(kierto + luku)
    saturaatio = saturoi(saturaatio + luku)
    print(f"lisätään {luku / SKAALA:+.2f}: kierto {kierto / SKAALA:+.4f}, "
          f"saturaatio {saturaatio / SKAALA:+.4f}")
print(f"oikea summa {sum(luvut) / SKAALA:+.4f}")
# @loppu summat
