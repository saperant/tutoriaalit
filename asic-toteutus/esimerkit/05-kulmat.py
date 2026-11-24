"""Prosessikulmat ja OCV: asetus tarkistetaan hitaassa, pito nopeassa.

Valmistusvaihtelu, käyttöjännite ja lämpötila muuttavat viiveitä.
Kirjastosta on yleensä erilliset versiot kulmille (esim. ss, tt, ff);
tässä kulma mallinnetaan kertoimella. Lisäksi saman piirin sisäinen
vaihtelu (on-chip variation, OCV) huomioidaan hidastamalla myöhäisiä
ja nopeuttamalla aikaisia polkuja.
"""

from pathlib import Path

from sta import Analyysi, Rajoitteet, pahimmat
from synteesi import syntetisoi

HAK = Path(__file__).parent

# @alku kulmat
KULMAT = {                       # viivekerroin suhteessa tyypilliseen
    "ss 1.62 V 125 °C": 1.35,
    "tt 1.80 V  25 °C": 1.00,
    "ff 1.98 V -40 °C": 0.72,
}
OCV = 0.08                       # ±8 % saman piirin sisällä
# @loppu kulmat


def main() -> None:
    kertoja = syntetisoi([HAK / "kertoja.v"], "kertoja")
    siirto = syntetisoi([HAK / "siirto.v"], "siirto")
    # @alku analyysi
    print("kulma              OCV   asetus (kertoja)   pito (siirto)")
    for kulma, k in KULMAT.items():
        for ocv in [0.0, OCV]:
            r = Rajoitteet(jakso=3.0, sisaan=0.3, myohainen=k * (1 + ocv),
                           aikainen=k * (1 - ocv),
                           kellon_viive={"q[2]": 0.20})
            asetus = pahimmat(Analyysi(kertoja, r).polut(), "asetus")[0]
            pito = pahimmat(Analyysi(siirto, r).polut(), "pito")[0]
            print(f"{kulma}  {ocv:4.0%}  {asetus.marginaali:+17.3f} "
                  f"{pito.marginaali:+15.3f}")
    # @loppu analyysi


if __name__ == "__main__":
    main()
