"""Vertaa C++-ketjua (08-reaaliaika) Python-viitteeseen samalla syotteella."""

import os
import shutil
import subprocess
from pathlib import Path

import numpy as np

import viite

ESIMERKIT = Path(__file__).resolve().parent.parent
LAHTEET = ["08-reaaliaika/lohkot.cpp", "08-reaaliaika/main.cpp"]

# @alku kaanna
ehdokkaat = [os.environ.get("CXX", ""), "g++-14", "g++", "clang++"]
kaantaja = next((k for k in ehdokkaat if k and shutil.which(k)), None)
if kaantaja is None:
    raise SystemExit("C++-kaantajaa ei loydy")
ohjelma = Path("ketju").resolve()
subprocess.run([kaantaja, "-std=c++23", "-O2", "-Wall", "-Wextra",
                "-Werror", "-o", str(ohjelma),
                *(str(ESIMERKIT / p) for p in LAHTEET)], check=True)
# @loppu kaanna

# @alku syote
# Kaksi aanta FM-moduloituna 200 kHz:iin, kohina ja 8 bitin kvantisointi.
rng = np.random.default_rng(8)
t = np.arange(200_000) / 912e3
viesti = 0.4 * np.sin(2 * np.pi * 1.3e3 * t) + 0.3 * np.sin(2 * np.pi * 7.1e3
                                                          * t)
vaihe = 2 * np.pi * (200e3 * t + 75e3 * np.cumsum(viesti) / 912e3)
z = 0.8 * np.exp(1j * vaihe)
z += 0.05 * (rng.standard_normal(len(t)) + 1j * rng.standard_normal(len(t)))
lomitettu = np.empty(2 * len(z))
lomitettu[0::2], lomitettu[1::2] = z.real, z.imag
cu8 = np.clip(np.round(lomitettu * 127.5 + 127.5), 0, 255).astype(np.uint8)
# @loppu syote

# @alku vertaa
tulos = subprocess.run([str(ohjelma), "--suodin", "200000"],
                       input=cu8.tobytes(), capture_output=True, check=True)
cpp = np.frombuffer(tulos.stdout, dtype=np.float32)
raaka = cu8.astype(np.float64)
zz = (raaka[0::2] - 127.5) / 127.5 + 1j * (raaka[1::2] - 127.5) / 127.5
py = viite.ketju(zz, 200e3)
ero = float(np.max(np.abs(cpp - py)))
print(f"naytteita: C++ {len(cpp)}, Python {len(py)}")
print(f"suurin ero {'<=' if ero <= 1e-5 else '>'} 1e-5: "
      f"{'OK' if ero <= 1e-5 and len(cpp) == len(py) else 'VIRHE'}")
# @loppu vertaa
