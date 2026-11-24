"""CAN:n vikojen rajaus: virhelaskurit ja solmun tilat."""

from mallit.can import Virhelaskurit

# @alku rikki
# Solmun lähetin on rikki: jokainen lähetysyritys päättyy virheeseen.
solmu = Virhelaskurit()
edellinen = solmu.tila
print("yritys  TEC  tila")
for yritys in range(1, 40):
    solmu.lahetysvirhe()
    if solmu.tila != edellinen or yritys in (1, 15):
        print(f"{yritys:6} {solmu.tec:4}  {solmu.tila}")
        edellinen = solmu.tila
    if solmu.tila == "bus-off":
        break
solmu.palaa(resessiivisia_jaksoja=128)
print(f"128 x 11 resessiivista bittia: TEC {solmu.tec}, {solmu.tila}")
# @loppu rikki

# @alku satunnainen
# Satunnaisia virheitä: yksi virhe kahdeksaa onnistumista kohti pitää
# TEC:n paikallaan (+8 - 8), harvempi virhe laskee sitä.
print()
for valein in (6, 8, 12):
    solmu = Virhelaskurit()
    kehys = 0
    while kehys < 900 and solmu.tila != "bus-off":
        kehys += 1
        if kehys % (valein + 1) == 0:
            solmu.lahetysvirhe()
        else:
            solmu.lahetys_ok()
    print(f"virhe joka {valein + 1:2}. kehyksessa: {kehys:3} kehyksen "
          f"jalkeen TEC {solmu.tec:3}, {solmu.tila}")
# @loppu satunnainen
