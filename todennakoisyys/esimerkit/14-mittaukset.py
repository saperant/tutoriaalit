"""Suorituskykymittaukset: keskiarvo, mediaani, persentiilit ja hännät."""

import numpy as np
import numpy.typing as npt

rng = np.random.default_rng(1234)


# @alku viiveet
def viiveita(n: int) -> npt.NDArray[np.float64]:
    """Palvelun vasteajat (ms): yleensä nopea, joskus hidas (2 %)."""
    nopea = rng.lognormal(mean=np.log(20.0), sigma=0.3, size=n)
    hidas = rng.lognormal(mean=np.log(400.0), sigma=0.5, size=n)
    return np.where(rng.random(n) < 0.02, hidas, nopea)


x = viiveita(100_000)
p50, p95, p99, p999 = np.percentile(x, [50, 95, 99, 99.9])
print(f"keskiarvo {float(x.mean()):6.1f} ms")
print(f"mediaani  {float(p50):6.1f} ms")
print(f"p95       {float(p95):6.1f} ms")
print(f"p99       {float(p99):6.1f} ms")
print(f"p99.9     {float(p999):6.1f} ms")
# @loppu viiveet

# @alku toistot
# Montako mittausta tarvitaan? p99:n arvio heiluu pienillä otoksilla.
for n in (100, 1_000, 10_000):
    arviot = [float(np.percentile(viiveita(n), 99)) for _ in range(200)]
    ala, yla = np.percentile(arviot, [5, 95])
    print(f"n = {n:>6}: p99-arvion 90 %:n vaihteluväli"
          f" [{float(ala):5.0f}, {float(yla):5.0f}] ms")
# @loppu toistot

# @alku vertailu
# Kahden version vertailu: bootstrap-väli mediaanien erotukselle.
vanha = viiveita(2000)
uusi = viiveita(2000) * 0.95                 # todellisuudessa 5 % nopeampi
erot = []
for _ in range(5000):
    a = rng.choice(vanha, vanha.size)
    b = rng.choice(uusi, uusi.size)
    erot.append(float(np.median(b) - np.median(a)))
ala, yla = np.percentile(erot, [2.5, 97.5])
print(f"mediaanien ero {float(np.median(uusi) - np.median(vanha)):+.2f} ms,"
      f" 95 %:n väli [{float(ala):+.2f}, {float(yla):+.2f}] ms")
# @loppu vertailu
