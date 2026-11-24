"""Häntäviiveen vahvistuminen: pyyntö odottaa hitainta palvelinta."""

import numpy as np

# @alku teoria
# Jokainen palvelin vastaa hitaasti (yli p99) 1 %:n todennäköisyydellä.
# Jos käyttäjän pyyntö odottaa N palvelinta, se on hidas, jos yksikin on.
for n in (1, 10, 100):
    print(f"N = {n:3}: P(pyyntö hidas) = 1 - 0.99^{n} = {1 - 0.99**n:.3f}")
# @loppu teoria

# @alku simulointi
rng = np.random.default_rng(4321)
yksittaiset = rng.lognormal(np.log(20.0), 0.5, size=(50_000, 100))
raja = float(np.percentile(yksittaiset, 99))
kokonaiset = yksittaiset.max(axis=1)          # hajautus 100 palvelimelle
print(f"yksittäisen palvelimen p99 = {raja:.0f} ms; kokonaispyynnön"
      f" mediaani = {float(np.median(kokonaiset)):.0f} ms")
# Varapyyntö (hedged request): jos vastausta ei tule p95-ajassa,
# lähetetään toinen pyyntö ja käytetään nopeampaa.
p95 = float(np.percentile(yksittaiset, 95))
toinen = p95 + rng.lognormal(np.log(20.0), 0.5, size=yksittaiset.shape)
suojattu = np.minimum(yksittaiset, toinen).max(axis=1)
print(f"varapyynnöillä: mediaani {float(np.median(suojattu)):.0f} ms,"
      f" lisäkuorma {float(np.mean(yksittaiset > p95)):.1%}")
# @loppu simulointi
