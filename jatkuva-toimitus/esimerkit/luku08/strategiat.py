"""Neljä julkaisustrategiaa ja kolme uutta versiota.

Jokainen yhdistelmä ajetaan 300 kertaa. Tulos kertoo, kuinka usein
valvonta perui julkaisun ja montako pyyntöä ehti epäonnistua.
"""

from toimitus.julkaisu import STRATEGIAT, Asetelma, keskiarvot

VERSIOT = (
    ("ehjä versio, virheitä 0,1 %", 0.001),
    ("rikkinäinen versio, virheitä 5 %", 0.05),
    ("hienovarainen vika, virheitä 0,6 %", 0.006),
)

for otsikko, virhe in VERSIOT:
    print(otsikko)
    print(f"  {'strategia':<14}{'peruttu':>8}{'askelia':>9}"
          f"{'uudelle':>9}{'virheitä':>10}")
    for strategia in STRATEGIAT:
        peruttu, askelia, uudelle, virheita = keskiarvot(
            strategia, Asetelma(virhe_uusi=virhe), toistoja=300)
        print(f"  {strategia.nimi:<14}{peruttu:>8.0%}{askelia:>9.1f}"
              f"{uudelle:>9.0f}{virheita:>10.1f}")
