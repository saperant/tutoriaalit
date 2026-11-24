"""NumPy-taulukot C++:ssa ilman kopiointia."""

import gc

import kuva
import kuva_nb
import numpy as np


def main() -> None:
    # @alku kynnys
    k = np.array([[10, 200, 30], [140, 50, 250]], dtype=np.uint8)
    kuva.kynnysta(k, 128)
    print("kynnystetty paikallaan:\n", k)

    k2 = np.arange(12, dtype=np.uint8).reshape(3, 4) * 20
    kuva.kynnysta(k2[:, ::2], 100)          # viipale: askel 2 tavua
    print("vain parilliset sarakkeet:\n", k2)

    try:
        kuva.kynnysta(k.astype(np.float64), 128)
    except TypeError:
        print("float64 hylätty: TypeError")
    # @loppu kynnys

    # @alku sumennus
    s = kuva.sumenna([[0, 0, 0], [0, 9, 0], [0, 0, 0]])
    print("sumennettu", s.dtype, "\n", np.round(s, 2))
    # @loppu sumennus

    # @alku puskuri
    kehys = kuva.Kehys(2, 3)
    nakyma = kehys.taulukko()
    nakyma[1, :] = 7                   # kirjoitus C++:n muistiin
    print("C++ näkee:", kehys.summa(), "| omistaa:",
          nakyma.flags.owndata)
    del kehys
    gc.collect()
    print("näkymä pitää kehyksen elossa:", int(nakyma.sum()))
    # @loppu puskuri

    # @alku ndarray
    v = np.linspace(0.0, 1.0, 5, dtype=np.float32)
    print("nanobind summa:", kuva_nb.summa(v))
    print("viipale kopioiden:", kuva_nb.summa(v[::2]))
    try:
        kuva_nb.summa_tiukka(v[::2])         # ei yhtenäinen
    except TypeError:
        print("tiukka versio hylkää viipaleen: TypeError")
    # @loppu ndarray


if __name__ == "__main__":
    main()
