"""Miksi turbulenssia ei voi vain laskea auki.

Suurimmat pyörteet ovat kappaleen kokoisia (L), pienimmät Kolmogorovin
mittakaavan kokoisia: eta / L = Re^(-3/4). Suora simulointi tarvitsee
hilan, joka erottaa pienimmät, ja aika-askeleen, joka seuraa niitä."""

# @alku hinta
NOPEUS = 1e9            # ruutupäivityksiä sekunnissa (nopea työasema)
TAVUA_RUUTU = 4 * 8     # kolme nopeutta ja paine kaksoistarkkuudella


def suora_simulointi(reynolds: float) -> tuple[float, float, float]:
    """Hilapisteiden määrä, aika-askelten määrä yhtä läpivirtausta
    kohden ja niiden tulo. Suuruusluokka-arvio: vakiokertoimet ovat
    ykkösiä."""
    pisteita = reynolds ** (9 / 4)        # (L / eta)³
    askelia = reynolds ** (3 / 4)         # CFL: dt ~ eta / U
    return pisteita, askelia, pisteita * askelia


def kesto(sekunteja: float) -> str:
    """Kesto luettavassa yksikössä kahden merkitsevän numeron tarkkuudella."""
    for raja, yksikko in ((3.156e13, "milj. vuotta"), (3.156e7, "vuotta"),
                          (86400.0, "vrk"), (3600.0, "h"), (60.0, "min")):
        if sekunteja >= 2.0 * raja:
            maara = float(f"{sekunteja / raja:.2g}")
            return f"{maara:,.0f} {yksikko}".replace(",", " ")
    return f"{sekunteja:.0f} s"


print("      Re  hilapisteitä    muistia  askelia  laskenta-aika")
for reynolds in (1e3, 1e4, 1e5, 1e6, 1e7, 1e8):
    pisteita, askelia, tyo = suora_simulointi(reynolds)
    muisti = pisteita * TAVUA_RUUTU / 1e9
    print(f"{reynolds:8.0e} {pisteita:13.1e} {muisti:8.1e} Gt {askelia:8.1e}"
          f"  {kesto(tyo / NOPEUS):>16}")
# @loppu hinta
