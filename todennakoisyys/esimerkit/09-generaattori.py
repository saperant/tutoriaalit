"""Satunnaislukugeneraattorit: oma LCG, siemenet ja rinnakkaiset virrat."""

import numpy as np


# @alku lcg
class Lcg:
    """Lineaarinen kongruenssigeneraattori x' = (a x + c) mod 2^32."""

    def __init__(self, siemen: int) -> None:
        self.x = siemen

    def seuraava(self) -> int:
        self.x = (1664525 * self.x + 1013904223) % 2**32
        return self.x


g = Lcg(2026)
luvut = [g.seuraava() for _ in range(16)]
# Alin bitti vuorottelee: modulo 2^k -generaattorin alimpien bittien
# jakso on vain 2^k. Kolikonheitto x % 2 olisi täysin ennustettava.
print("alimmat bitit:", "".join(str(x & 1) for x in luvut))
print("ylimmät bitit:", "".join(str(x >> 31) for x in luvut))
# @loppu lcg

# @alku siemen
a = np.random.default_rng(123).random(3)
b = np.random.default_rng(123).random(3)
print("sama siemen, sama jono:", bool(np.array_equal(a, b)),
      np.round(a, 4).tolist())
# @loppu siemen

# @alku virrat
# Rinnakkaiset työt: SeedSequence.spawn tuottaa riippumattomat virrat.
# Siemenet 1, 2, 3 ... ovat tilastollisesti epäilyttävä korvike.
juuri = np.random.SeedSequence(2026)
virrat = [np.random.default_rng(s) for s in juuri.spawn(4)]
keskiarvot = [float(v.normal(size=100_000).mean()) for v in virrat]
print("virtojen keskiarvot:", " ".join(f"{k:+.4f}" for k in keskiarvot))
# @loppu virrat
