"""Kehystys tavuvirrassa: CRC-16/CCITT-FALSE ja COBS. Vastaa
laitteen tiedostoa 03-kehykset/kehys.c."""

EROTIN = 0x00


def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for tavu in data:
        crc ^= tavu << 8
        for _ in range(8):
            crc = (crc << 1 ^ 0x1021) if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return crc


# @alku cobs
def cobs_koodaa(data: bytes) -> bytes:
    """Jokainen nolla korvataan etäisyydellä seuraavaan nollaan."""
    tulos = bytearray([0])
    koodin_paikka = 0
    for tavu in data:
        if tavu != 0:
            tulos.append(tavu)
        if tavu == 0 or len(tulos) - koodin_paikka == 0xFF:
            tulos[koodin_paikka] = len(tulos) - koodin_paikka
            koodin_paikka = len(tulos)
            tulos.append(0)
    tulos[koodin_paikka] = len(tulos) - koodin_paikka
    return bytes(tulos)
# @loppu cobs


def cobs_pura(data: bytes) -> bytes:
    """Purkaa COBS-koodatun lohkon; ValueError, jos se on virheellinen."""
    tulos = bytearray()
    i = 0
    while i < len(data):
        koodi = data[i]
        if koodi == 0 or i + koodi > len(data):
            raise ValueError("virheellinen COBS")
        lohko = data[i + 1:i + koodi]
        if 0 in lohko:
            raise ValueError("nolla COBS-datassa")
        tulos += lohko
        i += koodi
        if koodi != 0xFF and i < len(data):
            tulos.append(0)
    return bytes(tulos)


# @alku kehys
def kehys(kuorma: bytes) -> bytes:
    """Hyötykuorma, CRC (suurin tavu ensin), COBS ja erotin."""
    crc = crc16(kuorma)
    return cobs_koodaa(kuorma + crc.to_bytes(2, "big")) + bytes([EROTIN])


def pura_virta(virta: bytes) -> list[bytes | str]:
    """Jakaa tavuvirran erottimen kohdalta ja purkaa kehykset. Virheel-
    linen kehys palautetaan virheen kuvauksena."""
    tulos: list[bytes | str] = []
    for osa in virta.split(bytes([EROTIN]))[:-1]:
        try:
            data = cobs_pura(osa)
        except ValueError as virhe:
            tulos.append(str(virhe))
            continue
        if len(data) < 3 or crc16(data) != 0:
            tulos.append("CRC ei tasmaa")
        else:
            tulos.append(data[:-2])
    return tulos
# @loppu kehys
