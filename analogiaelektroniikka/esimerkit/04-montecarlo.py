"""Komponenttitoleranssit Sallen-Key-suodattimessa: Monte Carlo.

Netlistiin kirjoitetaan 200 kopiota suodattimesta, kukin satunnaisin
komponenttiarvoin, ja yksi ngspice-ajo mittaa jokaisen rajataajuuden.
"""

import math

import numpy as np

from spice import lopeta, simuloi, vertaa

# @alku netlist
N, R, C1, C2 = 200, 11.254e3, 20e-9, 10e-9
tol_R, tol_C = 0.01, 0.05              # toleranssit (3 sigmaa)
rng = np.random.default_rng(2026)


def arvo(nimellinen: float, tol: float) -> float:
    return nimellinen * (1 + rng.normal(0, tol / 3))


rivit = ["monte carlo", "Vin in 0 DC 0 AC 1"]
for k in range(N):
    rivit += [f"R1_{k} in a{k} {arvo(R, tol_R):.6g}",
              f"R2_{k} a{k} b{k} {arvo(R, tol_R):.6g}",
              f"C1_{k} a{k} o{k} {arvo(C1, tol_C):.6g}",
              f"C2_{k} b{k} 0 {arvo(C2, tol_C):.6g}",
              # ihanteellinen seuraaja: jänniteohjattu jännitelähde
              f"E{k} o{k} 0 b{k} 0 1"]
rivit += [".control", "ac dec 400 300 3k"]
for k in range(N):
    # Kulmataajuus f0 on toisen kertaluvun alipäästössä se taajuus,
    # jolla vaihe on -90 astetta; -3 dB:n taajuus riippuu lisäksi Q:sta.
    rivit += [f"meas ac f{k} WHEN vdb(o{k})=-3.0103 FALL=1",
              f"meas ac n{k} WHEN vp(o{k})=-1.5707963 FALL=1"]
rivit += [".endc", ".end"]
tulos = simuloi("\n".join(rivit) + "\n")
f3 = np.array([tulos.arvot[f"f{k}"] for k in range(N)])
f0 = np.array([tulos.arvot[f"n{k}"] for k in range(N)])
# @loppu netlist

# @alku tilastot
for nimi, x in (("f0", f0), ("f-3dB", f3)):
    print(f"{nimi}: keskiarvo {x.mean():.0f} Hz, hajonta "
          f"{100 * x.std() / x.mean():.2f} %, väli "
          f"{x.min():.0f} ... {x.max():.0f} Hz")
# Ensimmäisen kertaluvun arvio: f0 ~ (R1 R2 C1 C2)^(-1/2), joten
# suhteellinen hajonta on puolet neljän riippumattoman hajonnan
# neliösummasta.
arvio = 0.5 * math.sqrt(2 * (tol_R / 3) ** 2 + 2 * (tol_C / 3) ** 2)
vertaa("hajonta f0", float(f0.std() / f0.mean()), arvio, "", 0.15)
# @loppu tilastot
lopeta()
