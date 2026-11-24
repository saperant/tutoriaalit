"""Miksi Ethernet-kehys on vähintään 64 tavua?

Jaetussa törmäysalueessa lähettäjän on huomattava törmäys vielä
lähettäessään. Kehyksen lähettämisen on siis kestettävä vähintään
signaalin edestakainen matka-aika verkon kauimpien asemien välillä.
Aikaviipale (slot time) on kiinteä bittimäärä, joten nopeuden kasvaessa
verkon suurin sallittu halkaisija pienenee.
"""

# @alku slotti
VIIVE_S_PER_M = 5e-9          # signaali kulkee noin 2/3 valonnopeudella


def suurin_halkaisija_m(nopeus_bit_s: float, viipale_bittia: int) -> float:
    """Halkaisija, jolla edestakainen matka kestää viipaleen verran
    (ilman toistimien, kytkentöjen ja häirintäsignaalin viiveitä)."""
    viipale_s = viipale_bittia / nopeus_bit_s
    return viipale_s / 2 / VIIVE_S_PER_M


for nimi, nopeus, viipale, todellinen in [
        ("10 Mbit/s", 10e6, 512, 2500),
        ("100 Mbit/s", 100e6, 512, 205),
        ("1 Gbit/s", 1e9, 512, None),
        ("1 Gbit/s + laajennus", 1e9, 4096, 200)]:
    raja = suurin_halkaisija_m(nopeus, viipale)
    sallittu = f"{todellinen} m" if todellinen else "–"
    print(f"{nimi:<21} viipale {viipale:>4} b: teoria {raja:6.0f} m,"
          f" standardi {sallittu}")
# @loppu slotti
