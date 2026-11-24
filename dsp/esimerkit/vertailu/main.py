"""C-toteutusten vertailu Python-referensseihin toleranssilla."""

import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

import numpy as np
from scipy import signal

import kirjasto as c
import mallit

# @alku taulukko
Tarkistus = tuple[str, float, Callable[[], float]]


def aja(tarkistukset: list[Tarkistus]) -> bool:
    """Tulostaa vain toleranssin ja tuloksen: itse ero voi vaihdella
    kaantajan ja prosessorin mukaan, joten sita ei verrata tulosteena."""
    kunnossa = True
    for nimi, toleranssi, mittaa in tarkistukset:
        ero = mittaa()
        ok = ero <= toleranssi
        kunnossa &= ok
        raja = "bitilleen" if toleranssi == 0 else f"<= {toleranssi:.0e}"
        print(f"{nimi:34s} {raja:10s} {'OK' if ok else f'VIRHE {ero:.1e}'}")
    return kunnossa
# @loppu taulukko


def main() -> int:
    rng = np.random.default_rng(2026)
    x = rng.standard_normal(5_000)
    with tempfile.TemporaryDirectory() as hak:
        lib = c.kaanna(Path(hak))
        # @alku tarkistukset
        h = signal.firwin(63, 0.2)
        sos = signal.ellip(8, 0.1, 80, 0.1, output="sos")
        hd = signal.firwin(48, 1 / 8)                   # 48 = 4 * 12
        hq = np.round(signal.firwin(15, 0.25) * 32768).astype(np.int16)
        xq = np.round(np.clip(x / 4, -1, 1) * 32767).astype(np.int16)
        e = rng.standard_normal(x.size) * 0.01
        d = signal.lfilter(signal.firwin(16, 0.3), [1.0], x) + e
        ref = signal.lfilter(h, [1.0], x)
        ero = mallit.suhteellinen_ero

        def lohkoittain() -> float:
            fir = c.Fir(lib, h)
            osat = [fir.kasittele(x[i:i + 37]) for i in range(0, x.size, 37)]
            return ero(np.concatenate(osat), c.Fir(lib, h).kasittele(x))

        def q15() -> float:
            saatu, sat_c = c.q15_prosessori(lib, hq, xq, 3 * 4096)
            malli, sat_py = mallit.q15_prosessori(hq, xq, 3 * 4096)
            samat = np.array_equal(saatu, malli) and sat_c == sat_py
            return 0.0 if samat else 1.0

        tarkistukset: list[Tarkistus] = [
            ("FIR vs. lfilter", 1e-12,
             lambda: ero(c.Fir(lib, h).kasittele(x), ref)),
            ("FIR symmetrinen vs. lfilter", 1e-12,
             lambda: ero(c.Fir(lib, h, True).kasittele(x), ref)),
            ("FIR lohkoittain vs. kerralla", 0.0, lohkoittain),
            ("SOS DF2T vs. sosfilt", 1e-10,
             lambda: ero(c.Sos(lib, sos, False).kasittele(x),
                         signal.sosfilt(sos, x))),
            ("SOS DF1 vs. sosfilt", 1e-10,
             lambda: ero(c.Sos(lib, sos, True).kasittele(x),
                         signal.sosfilt(sos, x))),
            ("RBJ-alipaasto vs. butter(2)", 1e-12,
             lambda: ero(c.rbj_alipaasto(lib, 1e3, 2**-0.5, 48e3),
                         signal.butter(2, 1e3, output="sos", fs=48e3)[0])),
            ("FFT vs. numpy.fft", 1e-12,
             lambda: ero(c.fft(lib, x[:4096].astype(np.complex128)),
                         np.fft.fft(x[:4096]))),
            ("desimoija vs. upfirdn", 1e-12,
             lambda: ero(c.Desimoija(lib, hd, 4).kasittele(x),
                         signal.upfirdn(hd, x, down=4)[:x.size // 4])),
            ("interpoloija vs. upfirdn", 1e-12,
             lambda: ero(c.Interpoloija(lib, 4 * hd, 4).kasittele(x),
                         signal.upfirdn(4 * hd, x, up=4)[:4 * x.size])),
            ("NLMS vs. Python-malli", 1e-9,
             lambda: ero(c.nlms(lib, x, d, 16, 0.5),
                         mallit.nlms(x, d, 16, 0.5))),
            ("Q15-kasittelija vs. malli", 0.0, q15),
        ]
        return 0 if aja(tarkistukset) else 1
        # @loppu tarkistukset


if __name__ == "__main__":
    sys.exit(main())
