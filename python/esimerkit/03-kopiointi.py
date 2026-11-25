"""Matala ja syvä kopio sisäkkäisille rakenteille."""

import copy

# @alku kopio
vuorot = [["Ada", "Bob"], ["Cia"]]     # lista listoja

matala = copy.copy(vuorot)             # uusi ulkolista, samat sisälistat
syva = copy.deepcopy(vuorot)           # myös sisälistat kopioidaan

vuorot[0].append("Dan")
vuorot.append(["Eli"])

print(matala)
print(syva)
# @loppu kopio

# @alku ruudukko
jaettu = [[0] * 3] * 3                 # kolme viittausta samaan riviin
jaettu[0][0] = 1
print(jaettu)

erilliset = [[0] * 3 for _ in range(3)]    # kolme eri riviä
erilliset[0][0] = 1
print(erilliset)
# @loppu ruudukko
