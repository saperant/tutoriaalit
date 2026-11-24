"""Sama luku kolmella algoritmilla: e^-20 Taylorin sarjasta."""

import math


# @alku sarja
def exp_sarja(x: float, termeja: int = 150) -> float:
    """e^x Taylorin sarjasta: summa x^k / k!, k = 0, 1, ..."""
    summa, termi = 0.0, 1.0
    for k in range(termeja):
        summa += termi
        termi *= x / (k + 1)
    return summa
# @loppu sarja


# @alku vertailu
tarkka = math.exp(-20.0)
suora = exp_sarja(-20.0)            # vuorottelevat termit, suurin ~4e7
kaanteinen = 1.0 / exp_sarja(20.0)  # vain positiivisia termejä
for nimi, arvo in [("suora sarja", suora), ("1 / sarja(20)", kaanteinen),
                   ("math.exp", tarkka)]:
    suht = abs(arvo - tarkka) / tarkka
    print(f"{nimi:14s} {arvo: .6e}  suhteellinen virhe {suht:.0e}")
# @loppu vertailu

# @alku syy
suurin = max(20.0**k / math.factorial(k) for k in range(60))
print(f"suurin termi {suurin:.2e}, tulos {tarkka:.2e}, "
      f"suhde {suurin / tarkka:.0e}")
print(f"pyöristysvirhe suurimmassa termissä ~ {suurin * 2**-53:.0e}")
# @loppu syy
