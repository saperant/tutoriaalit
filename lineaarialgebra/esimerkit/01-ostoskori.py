"""Ostoskori lineaarialgebrana: pistetulo ja matriisin ja vektorin tulo."""

import numpy as np

# @alku puhdas
Vektori = list[float]


def pistetulo(a: Vektori, b: Vektori) -> float:
    """Summa a[i] * b[i]; vektorien on oltava yhtä pitkiä."""
    if len(a) != len(b):
        raise ValueError(f"pituudet eroavat: {len(a)} ja {len(b)}")
    return sum(x * y for x, y in zip(a, b, strict=True))


hinnat = [2.49, 0.89, 3.95]          # maito, banaani, kahvi (€/kpl)
kori = [2.0, 6.0, 1.0]               # ostettu määrä
print(f"korin hinta: {pistetulo(hinnat, kori):.2f} €")
# @loppu puhdas

# @alku matriisi
# Jokainen rivi on yhden asiakkaan kori. Matriisin ja vektorin tulo
# laskee kaikkien korien hinnat yhdellä operaatiolla.
korit = [[2.0, 6.0, 1.0],
         [0.0, 12.0, 0.0],
         [1.0, 0.0, 2.0]]
summat = [pistetulo(rivi, hinnat) for rivi in korit]
print("korien hinnat:", ", ".join(f"{s:.2f}" for s in summat))

K = np.array(korit)
h = np.array(hinnat)
print("NumPy (K @ h):", ", ".join(f"{s:.2f}" for s in K @ h))
# @loppu matriisi

# @alku alennus
# Kampanja: banaanit -20 %. Hinnat kerrotaan diagonaalimatriisilla,
# joka skaalaa jokaista koordinaattia erikseen.
alennus = np.diag([1.0, 0.8, 1.0])
print("alennetut:", ", ".join(f"{s:.2f}" for s in K @ (alennus @ h)))
# @loppu alennus
