"""Lukujen C-toteutukset jaettuna kirjastona ctypesin kautta."""

import ctypes as ct
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

ESIMERKIT = Path(__file__).resolve().parent.parent
LAHTEET = ["05-fir/fir.c", "07-biquad/biquad.c", "08-fft/fft.c",
           "09-polyfaasi/polyfaasi.c", "10-lms/lms.c",
           "11-reaaliaika/prosessori.c"]
Liukuluvut = NDArray[np.float64]
PD = ct.POINTER(ct.c_double)
PI16 = ct.POINTER(ct.c_int16)


# @alku kaanna
def kaanna(kohde: Path) -> ct.CDLL:
    """Kaantaa C-lahteet jaetuksi kirjastoksi ja lataa sen."""
    ehdokkaat = [os.environ.get("CC", ""), "gcc-14", "gcc", "clang", "cc"]
    kaantaja = next((k for k in ehdokkaat if k and shutil.which(k)), None)
    if kaantaja is None:
        raise RuntimeError("C-kaantajaa ei loydy")
    so = kohde / "libdsp.so"
    subprocess.run([kaantaja, "-std=c23", "-O2", "-Wall", "-Wextra",
                    "-Werror", "-fPIC", "-shared", "-o", str(so),
                    *(str(ESIMERKIT / p) for p in LAHTEET), "-lm"],
                   check=True)
    lib = ct.CDLL(str(so))
    maarittele(lib)
    return lib
# @loppu kaanna


# @alku tyypit
def maarittele(lib: ct.CDLL) -> None:
    """Parametrien ja paluuarvon tyypit: ilman niita ctypes arvaa, ja
    vaara jarjestys kaataa ohjelman eika anna virheilmoitusta."""
    P, Z = ct.c_void_p, ct.c_size_t
    tyypit = {
        "fir_alusta": ([P, PD, Z, PD], ct.c_int),
        "fir_kasittele": ([P, PD, PD, Z], None),
        "fir_kasittele_symm": ([P, PD, PD, Z], None),
        "sos_alusta": ([P, P, Z, PD, ct.c_int], ct.c_int),
        "sos_kasittele": ([P, PD, PD, Z], None),
        "biquad_alipaasto": ([P, ct.c_double, ct.c_double, ct.c_double],
                             ct.c_int),
        "fft_alusta": ([P, Z, PD], ct.c_int),
        "fft_suorita": ([P, PD, ct.c_bool], None),
        "desimoija_alusta": ([P, PD, Z, Z, PD], ct.c_int),
        "desimoi": ([P, PD, Z, PD], Z),
        "interpoloija_alusta": ([P, PD, Z, Z, PD], ct.c_int),
        "interpoloi": ([P, PD, Z, PD], None),
        "nlms_alusta": ([P, Z, ct.c_double, PD, PD], ct.c_int),
        "nlms_askel": ([P, ct.c_double, ct.c_double, P], ct.c_double),
        "prosessori_alusta": ([P, PI16, Z, PI16, ct.c_int32], ct.c_int),
        "prosessori_lohko": ([P, PI16, PI16, Z], None),
    }
    for nimi, (argumentit, paluu) in tyypit.items():
        funktio = getattr(lib, nimi)
        funktio.argtypes = argumentit
        funktio.restype = paluu
# @loppu tyypit


def osoitin(a: NDArray[np.float64]) -> "ct._Pointer[ct.c_double]":
    if not (a.flags.c_contiguous and a.dtype == np.float64):
        raise TypeError("odotettiin yhtenaista float64-taulukkoa")
    return a.ctypes.data_as(PD)


# @alku rakenne
class FirT(ct.Structure):
    """Vastaa C:n tyyppia fir_t (05-fir/fir.h). Kenttien jarjestys ja
    tyypit on pidettava samoina kuin C:ssa."""

    _fields_ = [("h", PD), ("lkm", ct.c_size_t), ("viive", PD),
                ("paikka", ct.c_size_t)]
# @loppu rakenne


class BiquadT(ct.Structure):
    _fields_ = [(n, ct.c_double) for n in ("b0", "b1", "b2", "a1", "a2")]


class SosT(ct.Structure):
    _fields_ = [("lohkot", ct.POINTER(BiquadT)), ("lkm", ct.c_size_t),
                ("tila", PD), ("muoto", ct.c_int)]


class FftT(ct.Structure):
    _fields_ = [("n", ct.c_size_t), ("kertoimet", PD)]


class DesimoijaT(ct.Structure):
    _fields_ = [("h", PD), ("lkm", ct.c_size_t), ("M", ct.c_size_t),
                ("viive", PD), ("paikka", ct.c_size_t),
                ("vaihe", ct.c_size_t)]


class InterpoloijaT(ct.Structure):
    _fields_ = [("h", PD), ("lkm", ct.c_size_t), ("L", ct.c_size_t),
                ("viive", PD), ("paikka", ct.c_size_t)]


class NlmsT(ct.Structure):
    _fields_ = [("w", PD), ("viive", PD), ("lkm", ct.c_size_t),
                ("paikka", ct.c_size_t), ("mu", ct.c_double),
                ("eps", ct.c_double), ("energia", ct.c_double)]


class ProsessoriT(ct.Structure):
    _fields_ = [("h", PI16), ("lkm", ct.c_size_t), ("viive", PI16),
                ("paikka", ct.c_size_t), ("vahvistus", ct.c_int32),
                ("saturaatiot", ct.c_ulong)]


# @alku fir
class Fir:
    """C:n FIR-suodin; puskurit pidetaan elossa olion mukana."""

    def __init__(self, lib: ct.CDLL, h: Liukuluvut,
                 symmetrinen: bool = False) -> None:
        self._lib = lib
        self._h = np.ascontiguousarray(h, dtype=np.float64)
        self._viive = np.zeros(2 * self._h.size)
        self._s = FirT()
        if lib.fir_alusta(ct.byref(self._s), osoitin(self._h),
                          ct.c_size_t(self._h.size),
                          osoitin(self._viive)) != 0:
            raise ValueError("fir_alusta epaonnistui")
        nimi = "fir_kasittele_symm" if symmetrinen else "fir_kasittele"
        self._kasittele = getattr(lib, nimi)

    def kasittele(self, x: Liukuluvut) -> Liukuluvut:
        x = np.ascontiguousarray(x, dtype=np.float64)
        y = np.empty_like(x)
        self._kasittele(ct.byref(self._s), osoitin(x), osoitin(y),
                        ct.c_size_t(x.size))
        return y
# @loppu fir


class Sos:
    """C:n biquad-ketju SciPyn sos-taulukosta (b0 b1 b2 a0 a1 a2)."""

    def __init__(self, lib: ct.CDLL, sos: Liukuluvut, df1: bool) -> None:
        self._lib = lib
        self._lohkot = (BiquadT * len(sos))()
        for k, rivi in zip(self._lohkot, sos, strict=True):
            b0, b1, b2, a0, a1, a2 = (float(c) for c in rivi)
            k.b0, k.b1, k.b2 = b0 / a0, b1 / a0, b2 / a0
            k.a1, k.a2 = a1 / a0, a2 / a0
        self._tila = np.zeros(4 * len(sos))
        self._s = SosT()
        if lib.sos_alusta(ct.byref(self._s), self._lohkot,
                          ct.c_size_t(len(sos)), osoitin(self._tila),
                          0 if df1 else 1) != 0:
            raise ValueError("sos_alusta epaonnistui")

    def kasittele(self, x: Liukuluvut) -> Liukuluvut:
        x = np.ascontiguousarray(x, dtype=np.float64)
        y = np.empty_like(x)
        self._lib.sos_kasittele(ct.byref(self._s), osoitin(x), osoitin(y),
                                ct.c_size_t(x.size))
        return y


def rbj_alipaasto(lib: ct.CDLL, f0: float, q: float,
                  fs: float) -> Liukuluvut:
    """C:n biquad_alipaasto; palauttaa [b0, b1, b2, 1, a1, a2]."""
    k = BiquadT()
    if lib.biquad_alipaasto(ct.byref(k), ct.c_double(f0), ct.c_double(q),
                            ct.c_double(fs)) != 0:
        raise ValueError("virheellinen parametri")
    return np.array([k.b0, k.b1, k.b2, 1.0, k.a1, k.a2])


def fft(lib: ct.CDLL, x: NDArray[np.complex128],
        kaanteinen: bool = False) -> NDArray[np.complex128]:
    """C:n radix-2-FFT; x:n pituuden on oltava kahden potenssi."""
    tulos = np.array(x, dtype=np.complex128)   # kopio: muunnos paikallaan
    kertoimet = np.zeros(tulos.size // 2, dtype=np.complex128)
    s = FftT()
    if lib.fft_alusta(ct.byref(s), ct.c_size_t(tulos.size),
                      kertoimet.ctypes.data_as(PD)) != 0:
        raise ValueError("pituus ei ole kahden potenssi")
    lib.fft_suorita(ct.byref(s), tulos.ctypes.data_as(PD),
                    ct.c_bool(kaanteinen))
    return tulos


class Desimoija:
    def __init__(self, lib: ct.CDLL, h: Liukuluvut, M: int) -> None:
        self._lib = lib
        self._h = np.ascontiguousarray(h, dtype=np.float64)
        self._viive = np.zeros(2 * self._h.size)
        self._s = DesimoijaT()
        self._M = M
        if lib.desimoija_alusta(ct.byref(self._s), osoitin(self._h),
                                ct.c_size_t(self._h.size), ct.c_size_t(M),
                                osoitin(self._viive)) != 0:
            raise ValueError("desimoija_alusta epaonnistui")

    def kasittele(self, x: Liukuluvut) -> Liukuluvut:
        x = np.ascontiguousarray(x, dtype=np.float64)
        y = np.empty(x.size // self._M + 1)
        n = self._lib.desimoi(ct.byref(self._s), osoitin(x),
                              ct.c_size_t(x.size), osoitin(y))
        return y[:int(n)]


class Interpoloija:
    def __init__(self, lib: ct.CDLL, h: Liukuluvut, L: int) -> None:
        self._lib = lib
        self._h = np.ascontiguousarray(h, dtype=np.float64)
        self._viive = np.zeros(2 * (self._h.size // L))
        self._s = InterpoloijaT()
        self._L = L
        if lib.interpoloija_alusta(ct.byref(self._s), osoitin(self._h),
                                   ct.c_size_t(self._h.size),
                                   ct.c_size_t(L),
                                   osoitin(self._viive)) != 0:
            raise ValueError("kertoimien maaran on oltava L:n monikerta")

    def kasittele(self, x: Liukuluvut) -> Liukuluvut:
        x = np.ascontiguousarray(x, dtype=np.float64)
        y = np.empty(x.size * self._L)
        self._lib.interpoloi(ct.byref(self._s), osoitin(x),
                             ct.c_size_t(x.size), osoitin(y))
        return y


def nlms(lib: ct.CDLL, x: Liukuluvut, d: Liukuluvut, lkm: int,
         mu: float) -> Liukuluvut:
    """Ajaa C:n NLMS:n ja palauttaa virhesignaalin."""
    w, viive = np.zeros(lkm), np.zeros(2 * lkm)
    s = NlmsT()
    if lib.nlms_alusta(ct.byref(s), ct.c_size_t(lkm), ct.c_double(mu),
                       osoitin(w), osoitin(viive)) != 0:
        raise ValueError("nlms_alusta epaonnistui")
    e = np.empty(x.size)
    for n in range(x.size):
        e[n] = lib.nlms_askel(ct.byref(s), ct.c_double(x[n]),
                              ct.c_double(d[n]), None)
    return e


def q15_prosessori(lib: ct.CDLL, h: NDArray[np.int16],
                   x: NDArray[np.int16],
                   vahvistus: int) -> tuple[NDArray[np.int16], int]:
    """Ajaa Q1.15-kasittelijan; palauttaa ulostulon ja saturaatiot."""
    h = np.ascontiguousarray(h, dtype=np.int16)
    x = np.ascontiguousarray(x, dtype=np.int16)
    viive = np.zeros(2 * h.size, dtype=np.int16)
    y = np.empty_like(x)
    p = ProsessoriT()
    if lib.prosessori_alusta(ct.byref(p), h.ctypes.data_as(PI16),
                             ct.c_size_t(h.size),
                             viive.ctypes.data_as(PI16),
                             ct.c_int32(vahvistus)) != 0:
        raise ValueError("prosessori_alusta epaonnistui")
    lib.prosessori_lohko(ct.byref(p), x.ctypes.data_as(PI16),
                         y.ctypes.data_as(PI16), ct.c_size_t(x.size))
    return y, int(p.saturaatiot)
