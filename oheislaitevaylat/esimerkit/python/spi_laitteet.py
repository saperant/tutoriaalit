"""SPI-laitteita komentotasolla: NOR-flash ja ketjutetut rekisterit."""

from mallit.spi import ketju
from mallit.spiflash import PP, RDID, RDSR, READ, SE, WIP, WREN, SpiFlash

flash = SpiFlash()


# @alku jaljitys
def cs(tx: bytes, kuvaus: str) -> bytes:
    """Yksi transaktio CS:n laskusta nousuun, jäljitettynä kuten
    logiikka-analysaattorin SPI-dekooderi näyttää sen."""
    rx = flash.transaktio(tx)
    lyhyt = tx if len(tx) <= 6 else tx[:6]
    jatkuu = " .." if len(tx) > 6 else ""
    print(f"{kuvaus:24} MOSI {lyhyt.hex(' ')}{jatkuu}")
    if tx[0] in (RDID, READ):
        print(f"{'':24} MISO {rx[:6].hex(' ')}")
    return rx


def odota() -> int:
    """Tilarekisteriä kysytään, kunnes WIP nollautuu."""
    kyselyja = 1
    while flash.transaktio(bytes([RDSR, 0]))[1] & WIP:
        kyselyja += 1
    return kyselyja
# @loppu jaljitys


# @alku istunto
def osoite(a: int) -> bytes:
    return a.to_bytes(3, "big")


cs(bytes([RDID, 0, 0, 0]), "tunniste")
cs(bytes([PP]) + osoite(0x1000) + b"XY", "ohjelmointi ilman WREN")
cs(bytes([READ]) + osoite(0x1000) + bytes(2), "luku: ei muuttunut")
cs(bytes([WREN]), "salli kirjoitus")
cs(bytes([PP]) + osoite(0x10FE) + b"ABCD", "ohjelmoi 10fe: ABCD")
print(f"valmis {odota()} kyselyn jalkeen")
cs(bytes([READ]) + osoite(0x10FE) + bytes(2), "luku 10fe..10ff")
cs(bytes([READ]) + osoite(0x1000) + bytes(2), "luku 1000..1001")
cs(bytes([WREN]), "salli kirjoitus")
cs(bytes([SE]) + osoite(0x1000), "tyhjenna sektori 1000")
print(f"valmis {odota()} kyselyn jalkeen")
cs(bytes([READ]) + osoite(0x1000) + bytes(2), "luku 1000..1001")
# @loppu istunto

# @alku ketju
print()
print("kolme 8-bittista siirtorekisteria ketjussa")
for lahetetyt in ([0x01], [0x01, 0x02, 0x03]):
    tilat = ketju(lahetetyt, 3)
    print(f"lahetetty {bytes(lahetetyt).hex(' '):9} -> laitteet "
          f"{bytes(tilat).hex(' ')}")
# @loppu ketju
