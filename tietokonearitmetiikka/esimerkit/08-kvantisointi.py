"""Neuroverkon tiheän kerroksen int8-kvantisointi."""

import numpy as np
import numpy.typing as npt

Liuku = npt.NDArray[np.float32]
Int8 = npt.NDArray[np.int8]

# Toistettavat painot ja syöte ilman satunnaislukugeneraattoria.
rivit, sarakkeet = 16, 64
i, j = np.meshgrid(np.arange(rivit), np.arange(sarakkeet), indexing="ij")
W = (0.5 * np.sin(0.37 * i + 0.11 * j * j)).astype(np.float32)
x = (np.cos(0.21 * np.arange(sarakkeet)) + 1.0).astype(np.float32)


# @alku symmetrinen
def kvantisoi_painot(w: Liuku) -> tuple[Int8, float]:
    """Symmetrinen kvantisointi: nollapiste 0, skaala suurimmasta."""
    skaala = float(np.max(np.abs(w))) / 127.0
    q = np.clip(np.round(w / skaala), -127, 127).astype(np.int8)
    return q, skaala
# @loppu symmetrinen


# @alku asymmetrinen
def kvantisoi_syote(v: Liuku) -> tuple[Int8, float, int]:
    """Asymmetrinen: arvoalue [min, max] kuvataan väliin [-128, 127]."""
    pienin, suurin = float(v.min()), float(v.max())
    skaala = (suurin - pienin) / 255.0
    nollapiste = int(round(-128 - pienin / skaala))
    q = np.clip(np.round(v / skaala) + nollapiste, -128, 127)
    return q.astype(np.int8), skaala, nollapiste
# @loppu asymmetrinen


qW, sW = kvantisoi_painot(W)
qx, sx, zx = kvantisoi_syote(x)
# @alku kerros
# Kertolaskut kokonaisluvuilla, kertymä int32:ssa; skaalaus lopuksi.
kertyma = qW.astype(np.int32) @ (qx.astype(np.int32) - zx)
y_int8 = kertyma.astype(np.float32) * (sW * sx)
y_float = W @ x
# @loppu kerros
virhe = np.max(np.abs(y_int8 - y_float)) / np.max(np.abs(y_float))
print(f"painot {W.nbytes} -> {qW.nbytes} tavua")
print(f"syötteen skaala {sx:.5f}, nollapiste {zx}")
print(f"suurin suhteellinen virhe {virhe:.1%}")
print("kertymän suurin itseisarvo", int(np.max(np.abs(kertyma))),
      "> int16:n raja 32767:", bool(np.max(np.abs(kertyma)) > 32767))
