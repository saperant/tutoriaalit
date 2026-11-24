"""Fourier-muunnoksen ominaisuudet."""

from collections.abc import Callable
from typing import Any

import numpy as np
from numpy.typing import NDArray

Taulukko = NDArray[np.floating[Any]]
Kompleksi = NDArray[np.complexfloating[Any, Any]]


def muunnos(x: Kompleksi | Taulukko, t: Taulukko, dt: float,
            f: Taulukko) -> Kompleksi:
    """X(f) = int x(t) e^(-i 2 pi f t) dt summana tasavälisessä hilassa."""
    ytimet = np.exp(-2j * np.pi * np.outer(f, t))   # rivi kullekin f
    return np.asarray(ytimet @ x * dt, dtype=np.complex128)


f = np.linspace(-4, 4, 81)
dt = 0.01
t = np.arange(-800, 801) * dt               # [-8, 8]


# @alku ominaisuudet
def tarkista(nimi: str, vasen: Kompleksi, oikea: Kompleksi) -> None:
    virhe = float(np.max(np.abs(vasen - oikea)))
    print(f"{nimi:28s} {'ok' if virhe < 1e-9 else f'virhe {virhe:.1e}'}")


def X(g: Callable[[Taulukko], Taulukko | Kompleksi]) -> Kompleksi:
    return muunnos(g(t), t, dt, f)


def g0(s: Taulukko) -> Taulukko:
    return np.exp(-np.pi * s**2)


t0, f0, a = 0.7, 1.5, 3.0
G = X(g0)
G_siirto = np.exp(-np.pi * (f - f0) ** 2)
tarkista("lineaarisuus",
         X(lambda s: 2 * g0(s) + 3 * g0(s - 1)),
         2 * G + 3 * X(lambda s: g0(s - 1)))
tarkista("aikasiirto: x(t - t0)",
         X(lambda s: g0(s - t0)), np.exp(-2j * np.pi * f * t0) * G)
tarkista("modulaatio: x e^(i2pi f0 t)",
         X(lambda s: g0(s) * np.exp(2j * np.pi * f0 * s)),
         np.asarray(G_siirto, dtype=np.complex128))
tarkista("skaalaus: x(a t)",
         X(lambda s: g0(a * s)),
         np.asarray(np.exp(-np.pi * (f / a) ** 2) / a, dtype=np.complex128))
tarkista("kosinimodulaatio",
         X(lambda s: g0(s) * np.cos(2 * np.pi * f0 * s)),
         np.asarray((np.exp(-np.pi * (f - f0) ** 2)
                     + np.exp(-np.pi * (f + f0) ** 2)) / 2,
                    dtype=np.complex128))
# @loppu ominaisuudet
