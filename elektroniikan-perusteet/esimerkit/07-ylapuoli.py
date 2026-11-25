"""Yläpuolen kytkin: N-kanava seuraa hilaa, P-kanava kytkee kunnolla."""

import math

from spice import lopeta, muotoile, simuloi, vertaa

# @alku seuraaja
# N-kanava yläpuolella on lähdeseuraaja: U_GS = U_ohjaus - U_kuorma.
# Transistori on kyllästysalueella, joten kuorman virta U/R on
# K/2 (U_GS - U_th)^2. Toisen asteen yhtälö kuorman jännitteelle:
K, U_TH, R, U_OHJAUS = 10.0, 1.6, 6.0, 3.3
u_ov = U_OHJAUS - U_TH                    # ylijännite, jos kuorma olisi 0 V
a, b, c = K / 2, -(K * u_ov + 1 / R), K / 2 * u_ov**2
u_kuorma = (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)
# @loppu seuraaja

tulos = simuloi("07-ylapuoli.cir").sarjat
print("ohjaus 3,3 V:")
# Kanavanpituusmodulaatio (LAMBDA) kasvattaa virtaa hieman.
vertaa("N-kanava", tulos["v(la)"][0], u_kuorma, "V", 0.03)
# @alku vertailu
u_n, u_p = tulos["v(la)"][0], tulos["v(lb)"][0]
print(f"  N-kanava: kuorma {u_n:.2f} V, transistorin häviö "
      f"{muotoile((12 - u_n) * u_n / R, 'W')}")
print(f"  P-kanava: kuorma {u_p:.2f} V, transistorin häviö "
      f"{muotoile((12 - u_p) * u_p / R, 'W')}, hila "
      f"{muotoile(tulos['v(gp)'][0], 'V')}")
print(f"ohjaus 0 V: P-kanavan hila {tulos['v(gp)'][1]:.1f} V, "
      f"kuorma {abs(tulos['v(lb)'][1]):.2f} V")
# @loppu vertailu
lopeta()
