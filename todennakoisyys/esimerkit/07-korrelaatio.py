"""Otoskovarianssi ja korrelaatiokerroin: mitä ne mittaavat ja mitä eivät."""

import numpy as np
import numpy.typing as npt

Taulukko = npt.NDArray[np.float64]
rng = np.random.default_rng(314)
n = 20_000


# @alku korrelaatio
def korrelaatio(x: Taulukko, y: Taulukko) -> float:
    """Pearsonin korrelaatiokerroin: kovarianssi jaettuna hajonnoilla."""
    dx, dy = x - x.mean(), y - y.mean()
    kov = float(np.sum(dx * dy)) / (x.size - 1)
    return kov / (float(x.std(ddof=1)) * float(y.std(ddof=1)))


def parit(rho: float) -> tuple[Taulukko, Taulukko]:
    """Kaksi normaalijakautunutta muuttujaa, joiden korrelaatio on rho."""
    x = rng.normal(size=n)
    y = rho * x + np.sqrt(1 - rho**2) * rng.normal(size=n)
    return x, y


for rho in (0.9, 0.5, 0.0, -0.7):
    x, y = parit(rho)
    print(f"tavoite {rho:+.1f}: r = {korrelaatio(x, y):+.2f},",
          f"np.corrcoef {float(np.corrcoef(x, y)[0, 1]):+.2f}")
# @loppu korrelaatio

# @alku yksikot
# Kovarianssi riippuu yksiköistä, korrelaatio ei.
x, y = parit(0.5)
viive_s, viive_ms = y, 1000 * y
print(f"kovarianssi: {float(np.cov(x, viive_s)[0, 1]):.2f} (s),",
      f"{float(np.cov(x, viive_ms)[0, 1]):.0f} (ms)")
print(f"korrelaatio: {korrelaatio(x, viive_s):.2f} (s),",
      f"{korrelaatio(x, viive_ms):.2f} (ms)")
# Summan varianssi: Var(X + Y) = Var(X) + Var(Y) + 2 Cov(X, Y).
vasen = float(np.var(x + y, ddof=1))
oikea = (float(np.var(x, ddof=1)) + float(np.var(y, ddof=1))
         + 2 * float(np.cov(x, y)[0, 1]))
print("Var(X + Y) = Var(X) + Var(Y) + 2 Cov(X, Y):",
      bool(np.isclose(vasen, oikea)))
# @loppu yksikot

# @alku epalineaarinen
# Korrelaatio mittaa vain suoraviivaista yhteyttä. Y = X^2 riippuu
# X:stä täysin, mutta korrelaatio on nolla, koska yhteys on symmetrinen.
x = rng.normal(size=n)
y = x**2
print(f"Y = X^2: r = {korrelaatio(x, y):+.2f}")
# Yksi poikkeava havainto voi yksin tuottaa korrelaation.
x, y = rng.normal(size=30), rng.normal(size=30)
print(f"30 riippumatonta paria: r = {korrelaatio(x, y):+.2f}")
print("sama ja yksi poikkeava piste (10, 10): r =",
      f"{korrelaatio(np.append(x, 10.0), np.append(y, 10.0)):+.2f}")
# @loppu epalineaarinen
