"""Symmetrinen matriisi ja pääkomponentit: anturidatan pääsuunta."""

import numpy as np

# @alku data
# Kiihtyvyysanturi värähtelee pääasiassa yhteen suuntaan, ja mittauksissa
# on kohinaa. Pääkomponentti löytää värähtelyn suunnan.
rng = np.random.default_rng(7)
t = rng.uniform(-1.0, 1.0, 500)
suunta = np.array([np.cos(np.radians(30)), np.sin(np.radians(30))])
data = np.outer(t * 3.0, suunta) + rng.normal(0.0, 0.3, (500, 2))
# @loppu data

# @alku pca
keskitetty = data - data.mean(axis=0)
C = keskitetty.T @ keskitetty / (len(data) - 1)       # kovarianssimatriisi
arvot, vektorit = np.linalg.eigh(C)                   # nousevassa järj.
print("C symmetrinen:", bool(np.allclose(C, C.T)))
print("ominaisvektorit kohtisuorassa:",
      bool(np.isclose(vektorit[:, 0] @ vektorit[:, 1], 0.0)))
paa = vektorit[:, -1] * np.sign(vektorit[0, -1])
kulma = np.degrees(np.arctan2(paa[1], paa[0]))
print(f"pääsuunta {kulma:.1f}° (todellinen 30°)")
print(f"pääkomponentti selittää {arvot[-1] / arvot.sum():.1%} varianssista")
# @loppu pca

# @alku definiitti
# Kovarianssimatriisi on positiivisesti definiitti: x^T C x > 0 kaikilla
# x != 0, eli kaikki ominaisarvot ovat positiivisia. Silloin
# Choleskyn hajotelma C = L L^T on olemassa.
print("ominaisarvot positiivisia:", bool(np.all(arvot > 0)))
kokeet = rng.normal(size=(1000, 2))
print("x^T C x > 0 tuhannella satunnaisella x:",
      bool(np.all(np.einsum("ij,jk,ik->i", kokeet, C, kokeet) > 0)))
L = np.linalg.cholesky(C)
print("Cholesky C = L L^T:", bool(np.allclose(L @ L.T, C)))
# @loppu definiitti
