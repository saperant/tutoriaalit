"""SPI bittitasolla: kellon napaisuus (CPOL) ja vaihe (CPHA).

Isäntä tuottaa kellon; CPOL on sen lepotaso. Kumpikin osapuoli
asettaa lähtönsä "siirtoreunalla" ja lukee toisen lähdön
"näytereunalla". Moodissa CPHA = 0 ensimmäinen bitti on linjalla jo
ennen ensimmäistä reunaa ja näyte otetaan jakson ensimmäisellä
reunalla; moodissa CPHA = 1 bitti asetetaan ensimmäisellä reunalla
ja luetaan toisella. Näytereuna on siis nouseva moodeissa 0 ja 3 ja
laskeva moodeissa 1 ja 2.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from mallit.aalto import Aalto


# @alku osapuoli
@dataclass
class Osapuoli:
    """Isäntä tai laite: lähetettävät bitit ja vastaanotetut bitit."""

    moodi: int
    lahtevat: list[int]
    saadut: list[int] = field(default_factory=list)
    lahto: int = 1

    @property
    def cpha(self) -> int:
        return self.moodi & 1

    def nayttaa(self, nouseva: bool) -> bool:
        """Näytteistetäänkö tällä reunalla? Osapuoli tuntee vain oman
        moodinsa: se ei tiedä, mikä kellon lepotaso todella on."""
        cpol = self.moodi >> 1
        return nouseva == (cpol == self.cpha)

    def seuraava(self) -> None:
        self.lahto = self.lahtevat.pop(0) if self.lahtevat else 1
# @loppu osapuoli


def bitit(tavut: Sequence[int], leveys: int = 8) -> list[int]:
    """Eniten merkitsevä bitti ensin, kuten SPI-laitteissa yleensä."""
    return [(t >> i) & 1 for t in tavut for i in reversed(range(leveys))]


def tavut(bittijono: Sequence[int], leveys: int = 8) -> list[int]:
    return [sum(b << (leveys - 1 - i)
                for i, b in enumerate(bittijono[k:k + leveys]))
            for k in range(0, len(bittijono) - leveys + 1, leveys)]


# @alku siirto
@dataclass
class Siirto:
    aalto: Aalto
    isannalle: list[int]  # isännän vastaanottamat tavut (MISO)
    laitteelle: list[int]  # laitteen vastaanottamat tavut (MOSI)


def siirto(mosi: Sequence[int], miso: Sequence[int], isannan_moodi: int,
           laitteen_moodi: int | None = None) -> Siirto:
    """Simuloi siirron reuna kerrallaan. Samalla reunalla näytteet
    otetaan ennen kuin lähdöt muuttuvat (pitoaika)."""
    laitteen_moodi = isannan_moodi if laitteen_moodi is None else \
        laitteen_moodi
    isanta = Osapuoli(isannan_moodi, bitit(mosi))
    laite = Osapuoli(laitteen_moodi, bitit(miso))
    cpol = isannan_moodi >> 1
    aalto = Aalto(["CS", "SCK", "MOSI", "MISO"])
    aalto.lisaa(1, cpol, 1, 1)
    for osapuoli in (isanta, laite):
        if osapuoli.cpha == 0:
            osapuoli.seuraava()  # ensimmäinen bitti ennen reunoja
    aalto.lisaa(0, cpol, isanta.lahto, laite.lahto)
    sck = cpol
    for reuna in range(2 * len(bitit(mosi))):
        sck ^= 1
        merkinta = ""
        if isanta.nayttaa(sck == 1):
            isanta.saadut.append(laite.lahto)
            merkinta = str(laite.lahto)
        if laite.nayttaa(sck == 1):
            laite.saadut.append(isanta.lahto)
        for osapuoli in (isanta, laite):
            # CPHA = 1 asettaa ensimmäisen bitin ensimmäisellä reunalla;
            # CPHA = 0 on asettanut sen jo ennen reunoja.
            ensimmainen = reuna == 0 and osapuoli.cpha == 0
            if not osapuoli.nayttaa(sck == 1) and not ensimmainen:
                osapuoli.seuraava()
        aalto.lisaa(0, sck, isanta.lahto, laite.lahto, merkinta=merkinta)
    aalto.lisaa(1, cpol, 1, 1)
    return Siirto(aalto, tavut(isanta.saadut), tavut(laite.saadut))
# @loppu siirto


# @alku ketju
def ketju(lahetetyt: Sequence[int], laitteita: int,
          alku: int = 0) -> list[int]:
    """Ketjutetut siirtorekisterit (daisy chain): jokaisen laitteen MISO
    on seuraavan MOSI. Siirron jälkeen kukin laite pitää viimeistä
    sinne asti työntynyttä tavua; palauttaa laitteiden tavut
    isännästä lukien."""
    rekisterit = [alku] * laitteita
    for tavu in lahetetyt:
        rekisterit = [tavu, *rekisterit[:-1]]
    return rekisterit
# @loppu ketju
