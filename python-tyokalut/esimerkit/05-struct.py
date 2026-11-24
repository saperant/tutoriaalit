"""Binääridatan perustyökalut: struct, tavujärjestys, kohdistus ja
bittikentät."""

import struct

# @alku jarjestys
arvo = 0x12345678
print("pieni-endian:", arvo.to_bytes(4, "little").hex(" "))
print("iso-endian:  ", arvo.to_bytes(4, "big").hex(" "))
print("verkko (!I): ", struct.pack("!I", arvo).hex(" "))
# @loppu jarjestys

# @alku kohdistus
# '@' = C-kääntäjän asettelu (täyte, alustan tavujärjestys),
# '<' ja '>' = tiivis, tavujärjestys kiinteä. Tiedostoissa ja
# protokollissa käytetään aina jälkimmäisiä.
for muoto in ("@BI", "<BI", ">BI"):
    print(f"{muoto}: {struct.calcsize(muoto)} tavua")
# @loppu kohdistus

# @alku otsake
# Paketti: tyyppi (u8), liput (u8), pituus (u16), aikaleima (u32),
# kaikki iso-endian. Struct-olio käännetään kerran ja käytetään usein.
OTSAKE = struct.Struct(">BBHI")
raaka = OTSAKE.pack(0x02, 0b1010_0001, 512, 1_700_000_000)
tyyppi, liput, pituus, aika = OTSAKE.unpack(raaka)
print(f"{OTSAKE.size} tavua: {raaka.hex(' ')}")
print(f"tyyppi {tyyppi}, liput {liput:08b}, pituus {pituus}, aika {aika}")
# @loppu otsake

# @alku bitit
# Tilarekisterin kentät: nimi -> (ylin bitti, alin bitti).
STATUS = {"VALMIS": (0, 0), "VIRHE": (1, 1), "TILA": (4, 2),
          "JONO": (15, 8)}


def pura(arvo: int, kentat: dict[str, tuple[int, int]]) -> dict[str, int]:
    tulos = {}
    for nimi, (ylin, alin) in kentat.items():
        leveys = ylin - alin + 1
        tulos[nimi] = (arvo >> alin) & ((1 << leveys) - 1)
    return tulos


def kokoa(arvot: dict[str, int], kentat: dict[str, tuple[int, int]]) -> int:
    sana = 0
    for nimi, arvo in arvot.items():
        ylin, alin = kentat[nimi]
        if arvo >> (ylin - alin + 1):
            raise ValueError(f"{nimi}={arvo} ei mahdu kenttään")
        sana |= arvo << alin
    return sana


rekisteri = 0x0A15
print(pura(rekisteri, STATUS))
print(hex(kokoa({"VALMIS": 1, "TILA": 5, "JONO": 10}, STATUS)))
# @loppu bitit
