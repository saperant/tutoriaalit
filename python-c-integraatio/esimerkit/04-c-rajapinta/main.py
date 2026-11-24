"""C++-kirjasto C-rajapinnan kautta: Python-luokka omistaa kahvan ja
vapauttaa sen varmasti."""

import ctypes
import weakref
from collections.abc import Sequence
from pathlib import Path
from types import TracebackType
from typing import Self

POLKU = Path(__file__).resolve().parents[1] / "build" / "libsuodatin.so"
lib = ctypes.CDLL(str(POLKU))
lib.suodatin_api_versio.restype = ctypes.c_int
lib.suodatin_luo.argtypes = [ctypes.c_size_t,
                             ctypes.POINTER(ctypes.c_void_p)]
lib.suodatin_luo.restype = ctypes.c_int
lib.suodatin_syota.argtypes = [ctypes.c_void_p,
                               ctypes.POINTER(ctypes.c_double),
                               ctypes.POINTER(ctypes.c_double),
                               ctypes.c_size_t]
lib.suodatin_syota.restype = ctypes.c_int
lib.suodatin_tuhoa.argtypes = [ctypes.c_void_p]
lib.suodatin_tuhoa.restype = None
lib.suodatin_virheviesti.argtypes = [ctypes.c_int]
lib.suodatin_virheviesti.restype = ctypes.c_char_p

VERSIO = 1


class SuodatinVirhe(RuntimeError):
    pass


def tarkista(tila: int) -> None:
    if tila != 0:
        viesti: bytes = lib.suodatin_virheviesti(tila)
        raise SuodatinVirhe(viesti.decode())


# @alku kaare
class Suodatin:
    """Liukuva keskiarvo. Kahva vapautetaan close():lla, with-lohkon
    lopussa tai viimeistään, kun olio kerätään roskana."""

    def __init__(self, ikkuna: int) -> None:
        if lib.suodatin_api_versio() != VERSIO:
            raise SuodatinVirhe("kirjaston rajapintaversio ei täsmää")
        kahva = ctypes.c_void_p()
        tarkista(lib.suodatin_luo(ikkuna, ctypes.byref(kahva)))
        self._kahva: int | None = kahva.value
        self._vapautus = weakref.finalize(self, lib.suodatin_tuhoa,
                                          kahva.value)

    def syota(self, arvot: Sequence[float]) -> list[float]:
        if self._kahva is None:
            raise ValueError("suodatin on suljettu")
        n = len(arvot)
        sisaan = (ctypes.c_double * n)(*arvot)
        ulos = (ctypes.c_double * n)()
        tarkista(lib.suodatin_syota(self._kahva, sisaan, ulos, n))
        return list(ulos)

    def close(self) -> None:
        self._kahva = None
        self._vapautus()          # kutsuu suodatin_tuhoa vain kerran

    def __enter__(self) -> Self:
        return self

    def __exit__(self, tyyppi: type[BaseException] | None,
                 arvo: BaseException | None,
                 jalki: TracebackType | None) -> None:
        self.close()
# @loppu kaare


def main() -> None:
    with Suodatin(3) as s:
        print("suodatettu:", s.syota([3.0, 6.0, 9.0, 12.0]))
        print("jatkuu:", s.syota([15.0]))
    try:
        s.syota([1.0])
    except ValueError as e:
        print("suljettu:", e)
    try:
        Suodatin(0)
    except SuodatinVirhe as e:
        print("ikkuna 0:", e)


if __name__ == "__main__":
    main()
