"""SPI:n neljä moodia ja väärin valitun moodin oire."""

from mallit.spi import siirto

# @alku aallot
for moodi in (0, 3):
    s = siirto([0xA5], [0x3C], moodi)
    print(f"moodi {moodi} (CPOL {moodi >> 1}, CPHA {moodi & 1}): "
          f"isanta sai {s.isannalle[0]:#04x}, laite sai "
          f"{s.laitteelle[0]:#04x}")
    print(s.aalto.piirra(askel=3))
    print()
# @loppu aallot

# @alku ristiin
def oire(saatu: int, odotettu: int) -> str:
    if saatu == odotettu:
        return "ok"
    if saatu & 0x7F == odotettu >> 1:
        return "bitti myohassa"
    return "vaarin"


print("isanta moodissa 0 lahettaa 0xa5, laite 0x3c")
print("laitteen moodi  isanta sai        laite sai")
for laite in range(4):
    s = siirto([0xA5], [0x3C], 0, laite)
    isannalle, laitteelle = s.isannalle[0], s.laitteelle[0]
    print(f"{laite:9}       {isannalle:#04x} {oire(isannalle, 0x3C):14} "
          f"{laitteelle:#04x} {oire(laitteelle, 0xA5)}")
# @loppu ristiin
