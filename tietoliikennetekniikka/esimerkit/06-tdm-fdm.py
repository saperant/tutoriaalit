"""Aika- ja taajuusjakoinen kanavointi (TDM ja FDM)."""

import numpy as np

# @alku tdm
# TDM: jokainen lähde saa kehyksessä oman aikavälinsä.
lahteet = {"A": "a1a2a3", "B": "b1b2b3", "C": "c1c2c3"}
kehykset = []
for i in range(3):
    kehykset.append("|".join(v[2 * i:2 * i + 2] for v in lahteet.values()))
print("TDM-kehykset:", " ".join(f"[{k}]" for k in kehykset))
erotettu = {nimi: "".join(k.split("|")[j] for k in kehykset)
            for j, nimi in enumerate(lahteet)}
print("erotettu:", erotettu)
# @loppu tdm

# @alku fdm
# FDM: kukin lähde moduloi omaa kantoaaltoaan; vastaanotin erottaa
# kanavan kertomalla oman kantoaallon kanssa ja keskiarvoistamalla.
naytteita, fs = 1000, 1000.0
t = np.arange(naytteita) / fs
kantoaallot = {"A": 50.0, "B": 120.0, "C": 200.0}
amplitudit = {"A": 1.0, "B": 0.5, "C": 0.25}       # lähetettävä tieto
signaali = sum(amplitudit[n] * np.cos(2 * np.pi * f * t)
               for n, f in kantoaallot.items())
for nimi, f in kantoaallot.items():
    arvio = 2 * float(np.mean(signaali * np.cos(2 * np.pi * f * t)))
    print(f"FDM-kanava {nimi} ({f:.0f} Hz): amplitudi {arvio:.3f}")
# @loppu fdm
