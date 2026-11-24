"""I2C bittitasolla: avokollektoriväylä, jolla on monta ohjaajaa.

Kumpikin linja on ylhäällä vain, jos kaikki osapuolet vapauttavat
sen (johdotettu JA). Simulaatio etenee aika-askelittain: jokainen
osapuoli päättää lähtönsä edellisen askeleen väylätilan perusteella,
ja väylän uusi tila on lähtöjen JA.
"""

from collections.abc import Generator, Sequence
from dataclasses import dataclass, field

from mallit.aalto import Aalto


# @alku vayla
@dataclass(frozen=True)
class Tila:
    scl: int = 1
    sda: int = 1


Lahto = tuple[int, int]  # (scl, sda): 1 = vapauta, 0 = vedä alas


class Osapuoli:
    def askel(self, vayla: Tila) -> Lahto:
        raise NotImplementedError


def simuloi(osapuolet: Sequence[Osapuoli], askelia: int,
            aalto: Aalto | None = None) -> Aalto:
    """Ajaa askelia aika-askelta. Jos aalto annetaan, simulaatio jatkuu
    sen viimeisestä tilasta (esim. uudella isännällä)."""
    if aalto is None:
        aalto = Aalto(["SCL", "SDA"])
        aalto.lisaa(1, 1)
    vayla = Tila(*aalto.naytteet[-1])
    for _ in range(askelia):
        lahdot = [o.askel(vayla) for o in osapuolet]
        vayla = Tila(min(s for s, _ in lahdot), min(d for _, d in lahdot))
        aalto.lisaa(vayla.scl, vayla.sda)
    return aalto
# @loppu vayla


Ohjelma = Generator[Lahto, Tila, None]


class Isanta(Osapuoli):
    """Isäntä ajaa ohjelmaa, joka tuottaa lähdön joka askeleella ja
    saa vastaukseksi väylän tilan."""

    def __init__(self, siirrot: Sequence[tuple[int, bytes, int]],
                 vapauta: bool = False, katkaise: int | None = None):
        """siirrot: (osoite, kirjoitettavat tavut, luettavien määrä).
        vapauta: kellota väylä ensin vapaaksi. katkaise: isäntä
        nollautuu (vapauttaa linjat) näin monen askeleen jälkeen."""
        self.loki: list[str] = []
        self.havisi = False
        self._katkaise = katkaise
        self._askelia = 0
        self._ohjelma = self._aja(siirrot, vapauta)
        next(self._ohjelma)

    def askel(self, vayla: Tila) -> Lahto:
        self._askelia += 1
        if self._katkaise is not None and self._askelia > self._katkaise:
            return (1, 1)
        try:
            return self._ohjelma.send(vayla)
        except StopIteration:
            return (1, 1)

    # @alku bitti
    def _bitti(self, arvo: int,
               valvo: bool = False) -> Generator[Lahto, Tila, int]:
        """Yksi kellojakso. valvo: isäntä lähettää bitin itse ja
        tarkistaa, että väylällä on sama arvo (arbitraatio)."""
        yield (0, arvo)  # SCL alhaalla: data saa vaihtua
        yield (0, arvo)
        vayla = yield (1, arvo)  # SCL vapaaksi
        while vayla.scl == 0:  # laite venyttää kelloa
            vayla = yield (1, arvo)
        if valvo and arvo == 1 and vayla.sda == 0:
            self.havisi = True  # joku muu vetää SDA:n alas
        yield (1, arvo)
        return vayla.sda

    def _tavu(self, tavu: int) -> Generator[Lahto, Tila, bool]:
        for i in reversed(range(8)):
            yield from self._bitti((tavu >> i) & 1, valvo=True)
            if self.havisi:
                return False
        return (yield from self._bitti(1)) == 0  # ACK = 0

    def _lue(self, kuittaa: bool) -> Generator[Lahto, Tila, int]:
        arvo = 0
        for _ in range(8):
            arvo = arvo << 1 | (yield from self._bitti(1))
        yield from self._bitti(0 if kuittaa else 1)
        return arvo
    # @loppu bitti

    def _havitty(self, osoite: int) -> Ohjelma:
        self.loki.append(f"{osoite:02x}: havisi arbitraation")
        while True:
            yield (1, 1)  # väylä jää voittajalle

    def _vapauta(self) -> Ohjelma:
        """Laite, joka jäi lähettämään tavua, pitää SDA:n alhaalla
        nollabitin kohdalla. Kellotetaan, kunnes se päästää irti
        (enintään yhdeksän jaksoa), ja päätetään STOPilla."""
        vayla = yield (1, 1)
        jaksoja = 0
        while vayla.sda == 0 and jaksoja < 9:
            vayla = Tila(1, (yield from self._bitti(1)))
            jaksoja += 1
        self.loki.append(f"vapautus: {jaksoja} kellojaksoa")
        yield from self._stop()

    def _start(self) -> Ohjelma:
        yield (1, 0)  # START: SDA laskee SCL:n ollessa ylhäällä
        yield (1, 0)
        yield (0, 0)

    def _stop(self) -> Ohjelma:
        yield (0, 0)  # STOP: SDA nousee SCL:n ollessa ylhäällä
        yield (1, 0)
        yield (1, 1)
        yield (1, 1)

    def _aja(self, siirrot: Sequence[tuple[int, bytes, int]],
             vapauta: bool) -> Ohjelma:
        yield (1, 1)
        if vapauta:
            yield from self._vapauta()
        for osoite, kirjoitus, luku_n in siirrot:
            yield from self._start()
            vaiheet = []
            if kirjoitus or not luku_n:
                vaiheet.append((osoite << 1, kirjoitus))
            if luku_n:
                vaiheet.append((osoite << 1 | 1, b""))
            for n, (osoitetavu, data) in enumerate(vaiheet):
                if n > 0:  # toistettu START: SDA ja SCL ensin ylös
                    yield (0, 1)
                    yield (1, 1)
                    yield from self._start()
                ok = yield from self._tavu(osoitetavu)
                for tavu in data:
                    if not ok:
                        break
                    ok = yield from self._tavu(tavu)
                if self.havisi:
                    yield from self._havitty(osoite)
                if not ok:
                    self.loki.append(f"{osoite:02x}: NACK")
                    break
                if osoitetavu & 1:
                    luettu = bytearray()
                    for i in range(luku_n):
                        kuittaa = i + 1 < luku_n
                        luettu.append((yield from self._lue(kuittaa)))
                    self.loki.append(f"{osoite:02x}: luettu "
                                     + luettu.hex(" "))
            yield from self._stop()


@dataclass
class Rekisterilaite(Osapuoli):
    """Laite, jolla on osoitinrekisteri: kirjoituksen ensimmäinen tavu
    valitsee rekisterin, ja luku jatkuu siitä eteenpäin."""

    osoite: int
    rekisterit: bytearray
    venytys: int = 0  # askelia, jotka laite pitää SCL:ää alhaalla
    _edellinen: Tila = field(default_factory=Tila)
    _bitit: int = 0
    _tavu: int = 0
    _vaihe: str = "lepo"  # lepo, osoite, kirjoitus, luku
    _valittu: bool = False
    _osoitin: int = 0
    _ensimmainen: bool = False
    _sda: int = 1
    _venyta: int = 0
    _lukuarvo: int = 0

    def askel(self, vayla: Tila) -> Lahto:
        e, self._edellinen = self._edellinen, vayla
        if e.scl and vayla.scl and e.sda and not vayla.sda:
            self._aloita()  # START tai toistettu START
        elif e.scl and vayla.scl and not e.sda and vayla.sda:
            self._vaihe, self._sda = "lepo", 1  # STOP
        elif not e.scl and vayla.scl and self._vaihe != "lepo":
            self._nouseva(vayla.sda)
        elif e.scl and not vayla.scl and self._vaihe != "lepo":
            self._laskeva()
        scl = 0 if self._venyta > 0 else 1
        self._venyta = max(0, self._venyta - 1)
        return (scl, self._sda)

    def _aloita(self) -> None:
        self._vaihe, self._bitit, self._tavu = "osoite", 0, 0
        self._sda = 1

    def _nouseva(self, sda: int) -> None:
        """Bitti luetaan SCL:n noustessa."""
        self._bitit += 1
        if self._bitit <= 8:
            self._tavu = self._tavu << 1 | sda
        elif self._vaihe == "luku" and sda == 1:
            self._vaihe = "lepo"  # isäntä vastasi NACK: luku päättyy

    def _laskeva(self) -> None:
        """Lähtö vaihdetaan SCL:n laskiessa."""
        if self._vaihe == "luku":
            if self._bitit == 9:  # edellinen tavu kuitattu: seuraava
                self._bitit = 0
                self._lukuarvo = self.rekisterit[self._osoitin]
                self._osoitin = (self._osoitin + 1) % len(self.rekisterit)
            self._sda = ((self._lukuarvo >> (7 - self._bitit)) & 1
                         if self._bitit < 8 else 1)
        elif self._bitit == 8:
            self._vastaanotettu()
        elif self._bitit == 9:
            self._bitit, self._tavu, self._sda = 0, 0, 1

    def _vastaanotettu(self) -> None:
        if self._vaihe == "osoite":
            if self._tavu >> 1 != self.osoite:
                self._vaihe = "lepo"
                return
            self._vaihe = "luku" if self._tavu & 1 else "kirjoitus"
            self._ensimmainen = True
        elif self._ensimmainen:
            self._osoitin, self._ensimmainen = self._tavu, False
        else:
            self.rekisterit[self._osoitin] = self._tavu
            self._osoitin = (self._osoitin + 1) % len(self.rekisterit)
        self._sda = 0  # ACK
        self._venyta = self.venytys


# @alku dekooderi
def dekoodaa(aalto: Aalto) -> str:
    """Logiikka-analysaattorin I2C-dekooderi: S = START, Sr = toistettu
    START, P = STOP, A/N = ACK/NACK, osoitteen perässä W tai R."""
    scl, sda = aalto.signaali("SCL"), aalto.signaali("SDA")
    osat: list[str] = []
    bitit: list[int] = []
    kaynnissa = False
    for t in range(1, len(scl)):
        if scl[t - 1] and scl[t] and sda[t - 1] != sda[t]:
            if sda[t] == 0:
                osat.append("Sr" if kaynnissa else "S")
                kaynnissa, bitit = True, []
            else:
                osat.append("P")
                kaynnissa = False
        elif not scl[t - 1] and scl[t] and kaynnissa:
            bitit.append(sda[t])
            if len(bitit) == 9:
                tavu = sum(b << (7 - i) for i, b in enumerate(bitit[:8]))
                ensimmainen = osat[-1] in ("S", "Sr")
                teksti = (f"{tavu >> 1:02x}{'R' if tavu & 1 else 'W'}"
                          if ensimmainen else f"{tavu:02x}")
                osat.append(teksti + (" N" if bitit[8] else " A"))
                bitit = []
    return " ".join(osat)
# @loppu dekooderi
