"""Lineaarinen regressio: suora pienimmällä neliösummalla ja jäännökset."""

import numpy as np
import numpy.typing as npt

Taulukko = npt.NDArray[np.float64]


# @alku sovitus
def sovita_suora(x: Taulukko, y: Taulukko) -> tuple[float, float]:
    """Pienimmän neliösumman suora y = a + b x:
    b = Cov(x, y) / Var(x) ja a = keskiarvo(y) - b keskiarvo(x)."""
    b = float(np.cov(x, y)[0, 1]) / float(np.var(x, ddof=1))
    return float(y.mean()) - b * float(x.mean()), b


def selitysaste(y: Taulukko, ennuste: Taulukko) -> float:
    """R^2: osuus y:n vaihtelusta, jonka malli selittää."""
    jaannos = float(np.sum((y - ennuste) ** 2))
    kokonais = float(np.sum((y - y.mean()) ** 2))
    return 1 - jaannos / kokonais
# @loppu sovitus


# @alku suora
# Mitattu: palvelimen kuorma (pyyntöä/s) ja suorittimen käyttöaste (%).
rng = np.random.default_rng(12)
kuorma = rng.uniform(50.0, 400.0, 60)
cpu = 8.0 + 0.15 * kuorma + rng.normal(0.0, 4.0, kuorma.size)

a, b = sovita_suora(kuorma, cpu)
jaannos = cpu - (a + b * kuorma)
r = float(np.corrcoef(kuorma, cpu)[0, 1])
print(f"cpu = {a:.2f} + {b:.4f} * kuorma")
print(f"r = {r:.3f}, r^2 = {r * r:.3f},",
      f"selitysaste = {selitysaste(cpu, a + b * kuorma):.3f}")
print(f"jäännösten keskiarvo {abs(float(jaannos.mean())):.3f},",
      f"keskihajonta {float(jaannos.std(ddof=2)):.2f} %-yks.")
# Sama tulos lineaarialgebran pienimmän neliösumman ratkaisijalla.
A = np.column_stack([np.ones_like(kuorma), kuorma])
kertoimet, *_ = np.linalg.lstsq(A, cpu, rcond=None)
print("lstsq antaa saman suoran:", bool(np.allclose(kertoimet, [a, b])))
print(f"ennuste kuormalla 300: {a + b * 300:.1f} %")
# @loppu suora

# @alku kayra
# Vasteaika kasvaa kuorman mukana jyrkkenevästi (jonoutuminen). Suora
# sopii kohtalaisesti, mutta jäännösten kuvio paljastaa väärän mallin.
kuorma2 = np.linspace(50.0, 400.0, 60)
vaste = 20.0 / (1 - kuorma2 / 500.0) + rng.normal(0.0, 3.0, kuorma2.size)
a2, b2 = sovita_suora(kuorma2, vaste)
jaannos2 = vaste - (a2 + b2 * kuorma2)
print(f"vasteaika: selitysaste {selitysaste(vaste, a2 + b2 * kuorma2):.2f}")
for nimi, osa in (("pieni", slice(0, 20)), ("keski", slice(20, 40)),
                  ("suuri", slice(40, 60))):
    print(f"  {nimi} kuorma: jäännösten keskiarvo"
          f" {float(jaannos2[osa].mean()):+6.1f} ms")
# @loppu kayra
