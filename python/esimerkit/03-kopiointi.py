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
