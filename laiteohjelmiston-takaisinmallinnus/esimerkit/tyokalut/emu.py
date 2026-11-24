"""Yksittäisten funktioiden ajaminen Unicornilla.

Laite-olio kartoittaa flash-kuvan, RAMin ja oheislaitealueen, ja
kutsu() ajaa yhden funktion AAPCS-kutsukonvention mukaan: argumentit
rekistereihin r0-r3, paluuosoite lr-rekisteriin. Kun funktio palaa
paluuosoitteeseen, ajo pysähtyy ja r0 on paluuarvo.
"""
import importlib
from collections.abc import Callable
from typing import Any

from unicorn import arm_const as a

# Unicornin Python-rajapinnan tyypitys on vajaa, joten se käytetään
# Any-tyyppisenä, ja tämän moduulin rajapinta on tyypitetty.
_uc: Any = importlib.import_module("unicorn")

FLASH, FLASH_KOKO = 0x00000000, 0x00040000
RAM, RAM_KOKO = 0x20000000, 0x00010000
OHEIS, OHEIS_KOKO = 0x40000000, 0x00030000
PALUU = 0x30000000            # paluuosoite: oma sivu, ei koodia
UART0_DATA, UART0_STATE = 0x40004000, 0x40004004
ARGUMENTIT = (a.UC_ARM_REG_R0, a.UC_ARM_REG_R1, a.UC_ARM_REG_R2,
              a.UC_ARM_REG_R3)


class Pysahdys(Exception):
    """Ajo pysähtyi valvottuun osoitteeseen (esim. vikakäsittelijään)."""

    def __init__(self, osoite: int) -> None:
        super().__init__(f"pysähtyi osoitteeseen {osoite:#x}")
        self.osoite = osoite


class Laite:
    """Cortex-M3 Unicornissa. Oheislaitteista mallinnetaan vain UART0:n
    lähetys: DATA-rekisteriin kirjoitetut tavut kerätään tulosteeseen,
    ja STATE-rekisteri kertoo aina, että lähetin on vapaa."""

    def __init__(self, flash: bytes) -> None:
        tila = _uc.UC_MODE_THUMB | _uc.UC_MODE_MCLASS
        self.uc: Any = _uc.Uc(_uc.UC_ARCH_ARM, tila)
        self.uc.mem_map(FLASH, FLASH_KOKO, _uc.UC_PROT_ALL)
        self.uc.mem_map(RAM, RAM_KOKO, _uc.UC_PROT_ALL)
        self.uc.mem_map(OHEIS, OHEIS_KOKO, _uc.UC_PROT_ALL)
        self.uc.mem_map(PALUU, 0x1000, _uc.UC_PROT_ALL)
        self.uc.mem_write(FLASH, flash[:FLASH_KOKO])
        self.tuloste = bytearray()
        self.kaskyja = 0
        self.pysahdykset: set[int] = set()
        self.uc.hook_add(_uc.UC_HOOK_MEM_WRITE, self._kirjoitus,
                         begin=OHEIS, end=OHEIS + OHEIS_KOKO - 1)
        self.uc.hook_add(_uc.UC_HOOK_MEM_READ, self._luku,
                         begin=OHEIS, end=OHEIS + OHEIS_KOKO - 1)
        self.uc.hook_add(_uc.UC_HOOK_CODE, self._kasky)

    # @alku hookit
    def _kirjoitus(self, uc: Any, tyyppi: int, osoite: int, koko: int,
                   arvo: int, _: object) -> None:
        if osoite == UART0_DATA:
            self.tuloste.append(arvo & 0xFF)

    def _luku(self, uc: Any, tyyppi: int, osoite: int, koko: int,
              arvo: int, _: object) -> None:
        if osoite == UART0_STATE:
            uc.mem_write(UART0_STATE, bytes(4))    # lähetin vapaa
    # @loppu hookit

    def _kasky(self, uc: Any, osoite: int, koko: int, _: object) -> None:
        self.kaskyja += 1
        if osoite in self.pysahdykset:
            uc.emu_stop()
            raise Pysahdys(osoite)

    def kirjoita(self, osoite: int, data: bytes) -> None:
        self.uc.mem_write(osoite, data)

    def lue(self, osoite: int, pituus: int) -> bytes:
        return bytes(self.uc.mem_read(osoite, pituus))

    def kutsu(self, funktio: int, *argumentit: int,
              raja: int = 2_000_000) -> int:
        """Ajaa funktion (osoite ilman Thumb-bittiä) ja palauttaa r0:n.
        Nostaa Pysahdys-poikkeuksen, jos ajo osuu valvottuun
        osoitteeseen."""
        for rekisteri, arvo in zip(ARGUMENTIT, argumentit):
            self.uc.reg_write(rekisteri, arvo & 0xFFFFFFFF)
        self.uc.reg_write(a.UC_ARM_REG_SP, RAM + RAM_KOKO - 0x100)
        self.uc.reg_write(a.UC_ARM_REG_LR, PALUU | 1)
        self.kaskyja = 0
        try:
            self.uc.emu_start(funktio | 1, PALUU, count=raja)
        except _uc.UcError as virhe:
            pc = self.uc.reg_read(a.UC_ARM_REG_PC)
            raise RuntimeError(f"{virhe} osoitteessa {pc:#x}") from virhe
        except Pysahdys:
            raise
        pc = int(self.uc.reg_read(a.UC_ARM_REG_PC))
        if pc != PALUU:
            raise RuntimeError(f"käskyraja täyttyi osoitteessa {pc:#x}")
        return int(self.uc.reg_read(a.UC_ARM_REG_R0))


def ajastettu(laite: Laite, kutsu: Callable[[], int]) -> tuple[int, int]:
    """Ajaa kutsun ja palauttaa (paluuarvo, käskyjen määrä)."""
    tulos = kutsu()
    return tulos, laite.kaskyja
