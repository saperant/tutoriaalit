"""C-kirjaston käyttö ctypesillä: tyypit, puskurit, ulostulo-
parametrit, errno, takaisinkutsut ja kirjaston varaama muisti."""

import ctypes
import errno
import os
import zlib
from pathlib import Path

# @alku lataus
POLKU = Path(__file__).resolve().parents[1] / "build" / "libtarkistus.so"
lib = ctypes.CDLL(str(POLKU), use_errno=True)

# Ilman argtypes/restype-määrittelyjä ctypes arvaa int-tyypit, mikä
# katkaisee osoittimet ja size_t-arvot 64-bittisellä alustalla.
lib.crc32_laske.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
lib.crc32_laske.restype = ctypes.c_uint32

lib.tilasto_laske.argtypes = [
    ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
]
lib.tilasto_laske.restype = ctypes.c_int
# @loppu lataus

# @alku takaisinkutsu-tyyppi
EDISTYMINEN = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_void_p)
lib.crc32_paloittain.argtypes = [
    ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t, EDISTYMINEN,
    ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32),
]
lib.crc32_paloittain.restype = ctypes.c_int
# @loppu takaisinkutsu-tyyppi

lib.heksana.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
lib.heksana.restype = ctypes.c_void_p   # ei c_char_p: osoite talteen
lib.heksana_vapauta.argtypes = [ctypes.c_void_p]
lib.heksana_vapauta.restype = None


# @alku kaareet
def crc32(data: bytes) -> int:
    return int(lib.crc32_laske(data, len(data)))


def tilasto(arvot: list[float]) -> tuple[float, float]:
    taulukko = (ctypes.c_double * len(arvot))(*arvot)
    ka = ctypes.c_double()
    hajonta = ctypes.c_double()
    if lib.tilasto_laske(taulukko, len(arvot),
                         ctypes.byref(ka), ctypes.byref(hajonta)) != 0:
        virhe = ctypes.get_errno()
        raise OSError(virhe, os.strerror(virhe))
    return ka.value, hajonta.value
# @loppu kaareet


# @alku paloittain
def crc32_edistyen(data: bytes, pala: int, raja: int | None) -> int:
    def edistyminen(tehty: int, yhteensa: int, _: int | None) -> int:
        print(f"  {tehty}/{yhteensa}")
        return 1 if raja is not None and tehty >= raja else 0

    kutsu = EDISTYMINEN(edistyminen)   # viite pidettävä elossa kutsun ajan
    tulos = ctypes.c_uint32()
    if lib.crc32_paloittain(data, len(data), pala, kutsu, None,
                            ctypes.byref(tulos)) != 0:
        virhe = ctypes.get_errno()
        raise OSError(virhe, os.strerror(virhe))
    return tulos.value
# @loppu paloittain


# @alku heksana
def heksana(data: bytes) -> str:
    osoite = lib.heksana(data, len(data))
    if not osoite:
        raise MemoryError
    try:
        return ctypes.string_at(osoite).decode("ascii")
    finally:
        lib.heksana_vapauta(osoite)   # kirjaston oma vapautus
# @loppu heksana


def main() -> None:
    data = b"Tutoriaalit testaavat jokaisen esimerkin."
    print(f"crc32: {crc32(data):08x} (zlib: {zlib.crc32(data):08x})")
    ka, hajonta = tilasto([20.1, 20.4, 19.8, 20.3])
    print(f"tilasto: keskiarvo {ka:.3f}, hajonta {hajonta:.3f}")
    try:
        tilasto([])
    except OSError as e:
        print("tyhjä:", errno.errorcode[e.errno or 0], "-", e.strerror)
    print("paloittain:")
    print(f"  tulos {crc32_edistyen(data, 16, None):08x}")
    try:
        crc32_edistyen(data, 16, 20)
    except OSError as e:
        print("  keskeytetty:", errno.errorcode[e.errno or 0])
    print("heksana:", heksana(b"\x00\x7f\xff"))


if __name__ == "__main__":
    main()
