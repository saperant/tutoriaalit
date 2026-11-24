"""Derivaatta erotusosamääränä: katkaisuvirhe ja pyöristysvirhe."""

import math

# @alku erotus
x0 = 1.0
tarkka = math.cos(x0)          # d/dx sin x = cos x
print("   h      eteenpäin    keskeinen")
for k in range(1, 15, 2):
    h = 10.0**-k
    eteen = (math.sin(x0 + h) - math.sin(x0)) / h
    keski = (math.sin(x0 + h) - math.sin(x0 - h)) / (2 * h)
    print(f"1e-{k:02d}  {abs(eteen - tarkka):.2e}   "
          f"{abs(keski - tarkka):.2e}")
# @loppu erotus

# @alku paras
# Eteenpäin-erotuksen virhe ~ h/2 |f''| + 2 eps |f| / h; pienin, kun
# h ~ sqrt(eps). Keskeiselle erotukselle h ~ eps^(1/3).
eps = 2.0**-52
print(f"sqrt(eps) = {math.sqrt(eps):.1e}, eps^(1/3) = {eps ** (1 / 3):.1e}")
# @loppu paras
