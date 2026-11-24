"""CAN 2.0A (11-bittinen tunniste) bittitasolla.

Väylällä 0 on dominantti ja 1 resessiivinen: jos yksikin solmu
lähettää nollan, väylä on nolla (johdotettu JA, kuten I2C:ssä).
"""

from collections.abc import Sequence
from dataclasses import dataclass

DOMINANTTI, RESESSIIVINEN = 0, 1
CRC15_POLYNOMI = 0x4599  # x^15 + x^14 + x^10 + x^8 + x^7 + x^4 + x^3 + 1


def bitit(arvo: int, leveys: int) -> list[int]:
    return [(arvo >> i) & 1 for i in reversed(range(leveys))]


def luku(bittijono: Sequence[int]) -> int:
    arvo = 0
    for b in bittijono:
        arvo = arvo << 1 | b
    return arvo


# @alku crc
def crc15(bittijono: Sequence[int]) -> int:
    """CRC-15 bitti kerrallaan, kuten standardin siirtorekisteri."""
    crc = 0
    for b in bittijono:
        takaisin = b ^ (crc >> 14)
        crc = (crc << 1) & 0x7FFF
        if takaisin:
            crc ^= CRC15_POLYNOMI
    return crc
# @loppu crc


# @alku kehys
@dataclass(frozen=True)
class Kehys:
    tunniste: int  # 0..0x7FF; pienempi voittaa arbitraation
    data: bytes = b""

    def __post_init__(self) -> None:
        if not 0 <= self.tunniste <= 0x7FF or len(self.data) > 8:
            raise ValueError("tunniste 11 bittia, dataa enintaan 8 tavua")

    def kentat(self) -> list[tuple[str, list[int]]]:
        """Kentät SOF:sta CRC:hen eli alue, jolle bittitäyttö tehdään."""
        kentat = [
            ("SOF", [DOMINANTTI]),
            ("ID", bitit(self.tunniste, 11)),
            ("RTR", [DOMINANTTI]),  # datakehys
            ("IDE", [DOMINANTTI]),  # 11-bittinen tunniste
            ("r0", [DOMINANTTI]),
            ("DLC", bitit(len(self.data), 4)),
            ("DATA", [b for t in self.data for b in bitit(t, 8)]),
        ]
        alku = [b for _, kentta in kentat for b in kentta]
        kentat.append(("CRC", bitit(crc15(alku), 15)))
        return kentat
# @loppu kehys


# @alku taytto
def tayta(bittijono: Sequence[int]) -> tuple[list[int], list[int]]:
    """Viiden samanarvoisen bitin jälkeen lisätään vastakkainen bitti.
    Palauttaa täytetyt bitit ja täytebittien paikat."""
    tulos: list[int] = []
    taytteet: list[int] = []
    perakkain = 0
    for b in bittijono:
        perakkain = perakkain + 1 if tulos and tulos[-1] == b else 1
        tulos.append(b)
        if perakkain == 5:
            taytteet.append(len(tulos))
            tulos.append(1 - b)
            perakkain = 1
    return tulos, taytteet


class Taytevirhe(ValueError):
    pass


def poista_taytto(bittijono: Sequence[int]) -> list[int]:
    tulos: list[int] = []
    perakkain = 0
    edellinen = -1
    ohita = False
    for i, b in enumerate(bittijono):
        if ohita:
            if b == edellinen:
                raise Taytevirhe(f"kuusi samaa bittia kohdassa {i}")
            ohita, edellinen, perakkain = False, b, 1
            continue
        perakkain = perakkain + 1 if b == edellinen else 1
        edellinen = b
        tulos.append(b)
        ohita = perakkain == 5
    return tulos
# @loppu taytto


# @alku linja
LOPPU = [RESESSIIVINEN] * 10  # CRC- ja ACK-erotin, ACK-paikka, EOF 7


def lahetettavat(kehys: Kehys) -> list[int]:
    """Lähettäjän bitit: täytetty alue ja kiinteä loppu. ACK-paikassa
    lähettäjä on resessiivinen; vastaanottajat kuittaavat sen."""
    alue = [b for _, kentta in kehys.kentat() for b in kentta]
    return tayta(alue)[0] + LOPPU


ACK_PAIKKA = -9  # LOPPU-osan toinen bitti lopusta laskien


def vastaanota(linja: Sequence[int]) -> Kehys:
    """Purkaa kehyksen väylän biteistä; Taytevirhe tai ValueError, jos
    kehys on virheellinen."""
    if linja[0] != DOMINANTTI:
        raise ValueError("ei SOF-bittia")
    alue = poista_taytto(linja[:-len(LOPPU)])
    dlc = luku(alue[15:19])
    pituus = 19 + 8 * dlc + 15
    if len(alue) != pituus:
        raise ValueError("vaara pituus")
    if crc15(alue[:pituus - 15]) != luku(alue[pituus - 15:]):
        raise ValueError("CRC-virhe")
    data = bytes(luku(alue[19 + 8 * i:27 + 8 * i]) for i in range(dlc))
    return Kehys(luku(alue[1:12]), data)
# @loppu linja


# @alku arbitraatio
@dataclass
class Arbitraatio:
    vayla: list[int]
    voittaja: int
    havisi: dict[int, int]  # solmu -> väylän bitti, jolla se luovutti


def arbitraatio(kehykset: Sequence[Kehys]) -> Arbitraatio:
    """Kaikki solmut aloittavat samalla bitillä. Solmu, joka lähettää
    resessiivisen mutta näkee dominantin, lopettaa ja jää
    kuuntelemaan."""
    jonot = [lahetettavat(k) for k in kehykset]
    lahettavat = set(range(len(kehykset)))
    havisi: dict[int, int] = {}
    vayla: list[int] = []
    i = 0
    while any(i < len(jonot[n]) for n in lahettavat):
        taso = min(jonot[n][i] for n in lahettavat)
        for n in sorted(lahettavat):
            if jonot[n][i] != taso:
                lahettavat.discard(n)
                havisi[n] = i
        vayla.append(taso)
        i += 1
    # Arbitraatiokenttä on SOF, tunniste ja RTR (13 bittiä ennen
    # täyttöä). Myöhempi ero on bittivirhe: kaksi solmua käytti samaa
    # tunnistetta.
    kentan_loppu = 13 + sum(1 for p in tayta(poista_taytto(vayla[:-10]))[1]
                            if p <= 13)
    if len(lahettavat) != 1 or any(p > kentan_loppu
                                   for p in havisi.values()):
        raise ValueError("samaa tunnistetta lahetti kaksi solmua")
    return Arbitraatio(vayla, lahettavat.pop(), havisi)
# @loppu arbitraatio


# @alku laskurit
@dataclass
class Virhelaskurit:
    """Vikojen rajaus: lähetysvirhe +8, onnistunut lähetys -1;
    vastaanottovirhe +1, onnistunut vastaanotto -1."""

    tec: int = 0
    rec: int = 0
    vaylalta: bool = False

    @property
    def tila(self) -> str:
        if self.vaylalta:
            return "bus-off"
        if self.tec >= 128 or self.rec >= 128:
            return "error passive"
        return "error active"

    def lahetysvirhe(self) -> None:
        self.tec += 8
        if self.tec > 255:
            self.vaylalta = True  # solmu irrottautuu väylästä

    def lahetys_ok(self) -> None:
        self.tec = max(0, self.tec - 1)

    def vastaanottovirhe(self) -> None:
        self.rec += 1

    def vastaanotto_ok(self) -> None:
        self.rec = 127 if self.rec > 127 else max(0, self.rec - 1)

    def palaa(self, resessiivisia_jaksoja: int) -> None:
        """Bus-off päättyy, kun väylällä on nähty 128 kertaa 11
        peräkkäistä resessiivistä bittiä."""
        if self.vaylalta and resessiivisia_jaksoja >= 128:
            self.tec, self.rec, self.vaylalta = 0, 0, False
# @loppu laskurit
