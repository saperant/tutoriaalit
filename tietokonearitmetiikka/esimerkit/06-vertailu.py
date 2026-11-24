"""Liukulukujen vertailu: suhteellinen ja absoluuttinen toleranssi."""

import math

# @alku vertailu
summa = sum([0.1] * 10)
print(summa, summa == 1.0, math.isclose(summa, 1.0))
# Suhteellinen toleranssi ei toimi nollan lähellä:
pieni = 1e-17
print(math.isclose(pieni, 0.0), math.isclose(pieni, 0.0, abs_tol=1e-12))
print(math.ulp(1.0), math.nextafter(1.0, 2.0))
# @loppu vertailu
