"""Laitteen uhkamalli: hyökkäyspinnat hyökkääjän pääsyn mukaan.

Palvelimen uhkamallissa hyökkääjä on verkossa. Laitteen hyökkääjä voi
myös ostaa laitteen, avata kotelon ja mitata piirilevyä. Malli
luettelee laitteen rajapinnat, kunkin vaatiman pääsyn ja vastatoimen,
ja laskee, mitkä pinnat kukin hyökkääjäprofiili tavoittaa.
"""

from dataclasses import dataclass
from enum import IntEnum


# @alku paasy
class Paasy(IntEnum):
    """Pääsytasot kasvavassa järjestyksessä.

    Korkeampi taso sisältää alemmat."""

    ETA = 1           # internet
    LAHI = 2          # sama lähiverkko, Bluetooth, radio
    FYYSINEN = 3      # laite käsissä: liittimet, debug-portit
    INVASIIVINEN = 4  # kotelo auki, piiri irti, mittalaitteet
# @loppu paasy


@dataclass(frozen=True)
class Pinta:
    nimi: str
    paasy: Paasy
    vastatoimi: str


@dataclass(frozen=True)
class Hyokkaaja:
    nimi: str
    paasy: Paasy
    laitteita: int      # montako laitetta hyökkäys koskee


# @alku pinnat
PINNAT = [
    Pinta("pilvirajapinta", Paasy.ETA, "TLS, laitekohtainen identiteetti"),
    Pinta("päivityspalvelu", Paasy.ETA, "allekirjoitetut kuvat"),
    Pinta("paikallinen web-käyttöliittymä", Paasy.LAHI,
          "ei oletussalasanaa"),
    Pinta("BLE-pariliitos", Paasy.LAHI, "todennettu pariliitos"),
    Pinta("UART-konsoli", Paasy.FYYSINEN, "konsoli pois tuotannossa"),
    Pinta("SWD/JTAG", Paasy.FYYSINEN, "debug-portin lukitus"),
    Pinta("ulkoinen flash", Paasy.FYYSINEN, "salaus ja allekirjoitus"),
    Pinta("virransyöttö (häiriöt)", Paasy.INVASIIVINEN,
          "kovennettu koodi, valvontapiiri"),
    Pinta("tehonkulutus (sivukanava)", Paasy.INVASIIVINEN,
          "vakioaikaisuus, maskaus"),
]
# @loppu pinnat

KANTA = 100_000   # laitteita kentällä

HYOKKAAJAT = [
    Hyokkaaja("botnetti", Paasy.ETA, KANTA),
    Hyokkaaja("naapuri", Paasy.LAHI, 1),
    Hyokkaaja("varas", Paasy.FYYSINEN, 1),
    Hyokkaaja("laboratorio", Paasy.INVASIIVINEN, 1),
]


# @alku arvioi
def tavoitettavat(h: Hyokkaaja) -> list[Pinta]:
    return [p for p in PINNAT if p.paasy <= h.paasy]


def vaikutus(h: Hyokkaaja, yhteinen_avain: bool) -> int:
    """Montako laitetta hyökkäys vaarantaa.

    Fyysinen hyökkäys kohdistuu yhteen laitteeseen, mutta jos siitä
    saadaan kaikille laitteille yhteinen salaisuus, se skaalautuu
    koko laitekantaan."""
    if h.paasy >= Paasy.FYYSINEN and yhteinen_avain:
        return KANTA
    return h.laitteita


def main() -> None:
    for h in HYOKKAAJAT:
        print(f"{h.nimi:12} {h.paasy.name:12} "
              f"{len(tavoitettavat(h))} pintaa, "
              f"vaikutus {vaikutus(h, True):>6} / {vaikutus(h, False)}")
    print("(vaikutus: yhteinen avain / laitekohtaiset avaimet)")
# @loppu arvioi


if __name__ == "__main__":
    main()
