"""SPI NOR -flashmuistin malli komentotasolla (vrt. 25-sarjan piirit).

Jokainen transaktio alkaa, kun CS laskee, ja päättyy, kun CS nousee.
Ensimmäinen tavu on komento; sitä seuraavat osoite ja data.
"""

from dataclasses import dataclass, field

# @alku komennot
RDID = 0x9F  # tunniste: valmistaja, tyyppi, koko
RDSR = 0x05  # tilarekisteri: bitti 0 WIP (kiire), bitti 1 WEL
WREN = 0x06  # kirjoituksen salliminen
PP = 0x02    # sivun ohjelmointi, enintään 256 tavua
SE = 0x20    # 4 KiB:n sektorin tyhjennys (tavut 0xFF:ksi)
READ = 0x03  # luku osoitteesta eteenpäin

WIP = 0x01
WEL = 0x02
SIVU = 256
SEKTORI = 4096
# @loppu komennot


# @alku malli
@dataclass
class SpiFlash:
    koko: int = 64 * 1024
    tunniste: bytes = bytes([0xEF, 0x40, 0x18])
    ohjelmointiaika: int = 2  # RDSR-kyselyä, joiden ajan WIP = 1
    tyhjennysaika: int = 5
    tila: int = 0
    kiire: int = 0
    muisti: bytearray = field(default_factory=bytearray)

    def __post_init__(self) -> None:
        self.muisti = bytearray([0xFF]) * self.koko

    def transaktio(self, tx: bytes) -> bytes:
        """Palauttaa MISO-tavut, yksi jokaista MOSI-tavua kohti."""
        komento, osoite = tx[0], int.from_bytes(tx[1:4], "big")
        if komento == RDSR:
            vastaus = bytes([0xFF, self.tila])
            if self.kiire > 0:
                self.kiire -= 1
                if self.kiire == 0:
                    self.tila &= ~(WIP | WEL)
            return vastaus.ljust(len(tx), bytes([self.tila]))
        if self.tila & WIP:
            return bytes([0xFF]) * len(tx)  # kiireinen piiri ei kuuntele
        if komento == RDID:
            return (bytes([0xFF]) + self.tunniste).ljust(len(tx), b"\xff")
        if komento == WREN:
            self.tila |= WEL
        elif komento == READ:
            data = self.muisti[osoite:osoite + len(tx) - 4]
            return bytes([0xFF] * 4) + bytes(data)
        elif komento in (PP, SE) and self.tila & WEL:
            if komento == PP:
                self._ohjelmoi(osoite, tx[4:])
                self.kiire = self.ohjelmointiaika
            else:
                alku = osoite - osoite % SEKTORI
                self.muisti[alku:alku + SEKTORI] = b"\xff" * SEKTORI
                self.kiire = self.tyhjennysaika
            self.tila |= WIP
        return bytes([0xFF]) * len(tx)

    def _ohjelmoi(self, osoite: int, data: bytes) -> None:
        """Ohjelmointi voi vain nollata bittejä, ja osoite kiertää
        sivun sisällä kuten oikeassa piirissä."""
        sivun_alku = osoite - osoite % SIVU
        for i, tavu in enumerate(data):
            paikka = sivun_alku + (osoite + i) % SIVU
            self.muisti[paikka] &= tavu
# @loppu malli
