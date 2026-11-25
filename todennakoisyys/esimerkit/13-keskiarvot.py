"""Kahden keskiarvon vertailu: Welchin testisuure ja permutaatiotesti."""

import math

import numpy as np

# @alku welch
# Käännösajat (s) kahdella kääntäjän asetuksella, 150 ajoa kummallakin.
rng = np.random.default_rng(606)
vanha = rng.normal(84.0, 6.0, 150)
uusi = rng.normal(82.5, 9.0, 150)

ero = float(uusi.mean() - vanha.mean())
# Welchin testisuure ei oleta ryhmille samaa varianssia.
kv = math.sqrt(float(vanha.var(ddof=1)) / vanha.size
               + float(uusi.var(ddof=1)) / uusi.size)
t = ero / kv
p_arvo = math.erfc(abs(t) / math.sqrt(2))     # normaaliapproksimaatio
print(f"ero {ero:+.2f} s, keskivirhe {kv:.2f} s, t = {t:.2f},",
      f"p = {p_arvo:.3f}")
print(f"95 %:n väli erolle [{ero - 1.96 * kv:+.2f},",
      f"{ero + 1.96 * kv:+.2f}] s")
# @loppu welch

# @alku permutaatio
kaikki = np.concatenate([vanha, uusi])
toistoja, yhta_suuria = 20_000, 0
for _ in range(toistoja):
    rng.shuffle(kaikki)
    sekoitettu = float(kaikki[150:].mean() - kaikki[:150].mean())
    yhta_suuria += abs(sekoitettu) >= abs(ero)
print(f"permutaatiotesti: p = {yhta_suuria / toistoja:.3f}")
# @loppu permutaatio
