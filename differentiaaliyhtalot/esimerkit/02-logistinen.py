"""Eksponentiaalinen ja logistinen kasvu."""

import sympy as sp

t = sp.symbols("t", nonnegative=True)
r, K, N0 = sp.symbols("r K N_0", positive=True)
N = sp.Function("N")

# @alku eksponentti
# Rajoittamaton kasvu: kasvunopeus on verrannollinen kokoon.
eksp = sp.dsolve(sp.Eq(N(t).diff(t), r * N(t)), N(t), ics={N(0): N0})
print("eksponentiaalinen:", eksp.rhs)
print("kaksinkertaistumisaika:", sp.solve(sp.Eq(eksp.rhs, 2 * N0), t)[0])
# @loppu eksponentti

# @alku logistinen
# Logistinen malli: kasvu hidastuu, kun koko lähestyy kantokykyä K.
logist = sp.dsolve(
    sp.Eq(N(t).diff(t), r * N(t) * (1 - N(t) / K)), N(t), ics={N(0): N0}
)
ratk = sp.simplify(logist.rhs)
print("logistinen:", ratk)
print("raja-arvo t -> oo:", sp.limit(ratk, t, sp.oo))
# Tarkistus: sijoitetaan ratkaisu takaisin yhtälöön.
jaannos = sp.simplify(ratk.diff(t) - r * ratk * (1 - ratk / K))
print("sijoitus yhtälöön:", jaannos)
# @loppu logistinen

# @alku kaannepiste
# Kasvunopeus rN(1 - N/K) on suurin, kun N = K/2.
n = sp.symbols("n", positive=True)
nopeus = r * n * (1 - n / K)
print(
    "suurin kasvunopeus kohdassa N =",
    sp.solve(nopeus.diff(n), n)[0],
    "arvo",
    sp.simplify(nopeus.subs(n, K / 2)),
)
# @loppu kaannepiste
