"""Persentiilejä ei voi laskea keskiarvona; histogrammit voi koota.

Kaksi palvelinta: A käsittelee 9 000 pyyntöä nopeasti, B 1 000
pyyntöä, joista osa on hitaita. Kumpikin raportoi oman p99-arvonsa.
Koko palvelun p99 lasketaan oikein vain yhdistetystä datasta tai
yhdistetystä histogrammista. Simulaatio käyttää kiinteää siementä.
"""

import random

from jarjestelma.histogrammi import Histogrammi, tarkka_kvantiili

RAJAT = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]


def main() -> None:
    s = random.Random(11)
    a = [s.uniform(0.005, 0.030) for _ in range(9000)]
    b = [s.uniform(0.010, 0.040) if s.random() < 0.9
         else s.uniform(0.3, 0.8) for _ in range(1000)]

    # @alku vertailu
    p99_a, p99_b = tarkka_kvantiili(a, 0.99), tarkka_kvantiili(b, 0.99)
    print(f"p99 A {p99_a * 1000:.0f} ms, B {p99_b * 1000:.0f} ms")
    print(f"p99-arvojen keskiarvo:        {(p99_a + p99_b) / 2 * 1000:4.0f}"
          " ms (väärin)")
    painotettu = (9000 * p99_a + 1000 * p99_b) / 10000
    print(f"painotettu keskiarvo:         {painotettu * 1000:4.0f}"
          " ms (väärin)")
    print(f"yhdistetystä datasta:         "
          f"{tarkka_kvantiili(a + b, 0.99) * 1000:4.0f} ms (oikein)")

    ha, hb = Histogrammi(RAJAT), Histogrammi(RAJAT)
    for arvo in a:
        ha.havainto(arvo)
    for arvo in b:
        hb.havainto(arvo)
    yhdistetty = ha.yhdista(hb)
    print(f"yhdistetystä histogrammista:  "
          f"{yhdistetty.kvantiili(0.99) * 1000:4.0f} ms"
          " (arvio lokeron sisällä)")
    # @loppu vertailu
    hitaat = sum(v > 0.25 for v in a + b) / len(a + b)
    print(f"yli 250 ms: {hitaat:.1%} pyynnöistä; SLO 'p99 < 250 ms'"
          f" {'täyttyy' if hitaat <= 0.01 else 'ei täyty'}")


if __name__ == "__main__":
    main()
