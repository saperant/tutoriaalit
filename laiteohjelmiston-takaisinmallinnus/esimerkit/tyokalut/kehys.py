"""LT-100:n kehykset huoltotyökalun puolelta (luvut 9 ja 11).

Kehys laitteelle (komento "kehys <heksa>"): tyyppi, pituus, data ja
CRC-16/CCITT (alkuarvo 0xFFFF, ei peilausta) isoin tavu ensin.

Käyttö: python3 kehys.py TYYPPI [DATA_HEKSANA]   tulostaa kehyksen
        heksana
"""
import sys


# @alku crc16
def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for tavu in data:
        crc ^= tavu << 8
        for _ in range(8):
            crc = (crc << 1) ^ 0x1021 if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return crc


def kehys(tyyppi: int, data: bytes) -> bytes:
    sisalto = bytes([tyyppi, len(data)]) + data
    return sisalto + crc16_ccitt(sisalto).to_bytes(2, "big")
# @loppu crc16


def main() -> None:
    tyyppi = int(sys.argv[1], 0)
    data = bytes.fromhex(sys.argv[2]) if len(sys.argv) > 2 else b""
    print(kehys(tyyppi, data).hex())


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
