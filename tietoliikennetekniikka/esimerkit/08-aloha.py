"""ALOHA: satunnaispääsy simuloituna ja analyyttisesti."""

import math

import numpy as np

rng = np.random.default_rng(11)


# @alku viipaloitu
def viipaloitu(kuorma: float, asemia: int = 100,
               viipaleita: int = 200_000) -> float:
    """Kukin asema lähettää viipaleessa todennäköisyydellä G/N.
    Viipale onnistuu, jos siinä lähettää tasan yksi asema."""
    lahettajia = rng.binomial(asemia, kuorma / asemia, viipaleita)
    return float(np.mean(lahettajia == 1))
# @loppu viipaloitu


# @alku puhdas
def puhdas(kuorma: float, kehyksia: int = 200_000) -> float:
    """Kehykset alkavat Poisson-prosessina (pituus 1). Kehys onnistuu,
    jos mikään muu kehys ei ala sitä edeltävän tai seuraavan
    kehysajan aikana."""
    alut = np.cumsum(rng.exponential(1 / kuorma, kehyksia))
    valit = np.diff(alut)
    ehja = (valit[1:] > 1) & (valit[:-1] > 1)
    return float(np.mean(ehja)) * kuorma
# @loppu puhdas


print("   G   viipaloitu (teoria)   puhdas (teoria)")
for g in (0.25, 0.5, 1.0, 2.0):
    print(f"{g:>4}  {viipaloitu(g):.3f} ({g * math.exp(-g):.3f})"
          f"         {puhdas(g):.3f} ({g * math.exp(-2 * g):.3f})")
print(f"maksimit: 1/e = {1 / math.e:.3f}, 1/(2e) = {1 / (2 * math.e):.3f}")
