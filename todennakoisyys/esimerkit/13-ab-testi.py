"""A/B-testi: kahden osuuden z-testi ja permutaatiotesti."""

import math

import numpy as np

# @alku data
# Versio A: 2000 käyttäjää, 200 konversiota. Versio B: 2000, 240.
na, ka_ = 2000, 200
nb, kb = 2000, 240
pa, pb = ka_ / na, kb / nb
# @loppu data

# @alku z
p = (ka_ + kb) / (na + nb)
kv = math.sqrt(p * (1 - p) * (1 / na + 1 / nb))
z = (pb - pa) / kv
p_arvo = math.erfc(abs(z) / math.sqrt(2))        # kaksisuuntainen
print(f"A {pa:.3f}, B {pb:.3f}, ero {pb - pa:+.3f}: z = {z:.2f},"
      f" p = {p_arvo:.4f}")
# @loppu z

# @alku permutaatio
# Permutaatiotesti: jos versioilla ei ole eroa, ryhmänimet voi
# sekoittaa. Kuinka usein sekoitettu ero on vähintään havaitun suuruinen?
rng = np.random.default_rng(77)
kaikki = np.r_[np.ones(ka_ + kb), np.zeros(na + nb - ka_ - kb)]
havaittu = pb - pa
toistoja, yhta_suuria = 20_000, 0
for _ in range(toistoja):
    rng.shuffle(kaikki)
    ero = float(kaikki[na:].mean() - kaikki[:na].mean())
    yhta_suuria += abs(ero) >= abs(havaittu) - 1e-12
print(f"permutaatiotesti: p = {yhta_suuria / toistoja:.4f}")
# @loppu permutaatio
