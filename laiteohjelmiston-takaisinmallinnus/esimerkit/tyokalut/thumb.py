"""Thumb-2-koodin purku Capstonella ja funktioiden etsintä.

Capstonella ei ole tyyppimäärittelyjä, joten se kääritään tähän
moduuliin, ja muut työkalut käyttävät vain tämän tietotyyppejä.
"""
import re
from dataclasses import dataclass, field

import capstone  # type: ignore[import-untyped]
from capstone import arm
from kuva import Kuva

_PURKAJA = capstone.Cs(capstone.CS_ARCH_ARM,
                       capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
_PURKAJA.detail = True


@dataclass(frozen=True)
class Kasky:
    osoite: int
    koko: int
    nimi: str            # esim. "ldr"
    operandit: str       # esim. "r3, [pc, #0x1c]"
    tavut: bytes
    kohde: int | None    # haaran kohde tai PC-suhteellisen luvun osoite
    lukee_pc: bool       # ldr rX, [pc, #n]: literaalivarannon luku
    vakio: int | None    # mov/movw/movt-käskyn välitön arvo

    def __str__(self) -> str:
        return f"{self.nimi:<7} {self.operandit}".rstrip()


def _kasky(raaka: object) -> Kasky:
    osoite = int(raaka.address)  # type: ignore[attr-defined]
    nimi = str(raaka.mnemonic)  # type: ignore[attr-defined]
    operandit = str(raaka.op_str)  # type: ignore[attr-defined]
    tavut = bytes(raaka.bytes)  # type: ignore[attr-defined]
    kohde: int | None = None
    vakio: int | None = None
    lukee_pc = False
    for op in raaka.operands:  # type: ignore[attr-defined]
        if op.type == arm.ARM_OP_IMM and _haara(nimi):
            kohde = int(op.imm)
        elif op.type == arm.ARM_OP_IMM and nimi in ("mov.w", "movw",
                                                    "movt"):
            vakio = int(op.imm) & 0xFFFFFFFF
        elif op.type == arm.ARM_OP_MEM and op.mem.base == arm.ARM_REG_PC:
            # PC luetaan Thumb-tilassa käskyn osoite + 4, sanaan
            # pyöristettynä.
            kohde = ((osoite + 4) & ~3) + int(op.mem.disp)
            lukee_pc = nimi.startswith("ldr")
    return Kasky(osoite, len(tavut), nimi, operandit, tavut, kohde,
                 lukee_pc, vakio)


def _haara(nimi: str) -> bool:
    return re.fullmatch(r"(b|bl|cbz|cbnz)(\.w|eq|ne|cs|hs|cc|lo|mi|pl|"
                        r"vs|vc|hi|ls|ge|lt|gt|le)?(\.w)?", nimi) is not None


def pura(kuva: Kuva, alku: int, maara: int) -> list[Kasky]:
    """Enintään maara käskyä osoitteesta alku (lineaarisesti)."""
    loppu = min(kuva.loppu, alku + 4 * maara)
    data = kuva.tavut(alku, loppu - alku)
    tulos = []
    for raaka in _PURKAJA.disasm(data, alku):
        tulos.append(_kasky(raaka))
        if len(tulos) == maara:
            break
    return tulos


def paluu(k: Kasky) -> bool:
    """Palaako käsky kutsujaan (bx lr tai pop, jossa on pc)."""
    if k.nimi == "bx" and k.operandit == "lr":
        return True
    return k.nimi.startswith("pop") and "pc" in k.operandit


@dataclass
class Funktio:
    osoite: int
    loppu: int = 0
    kutsuu: set[int] = field(default_factory=set)
    kaskyja: int = 0
    palautuu: bool = False
    hyppytaulut: dict[int, list[int]] = field(default_factory=dict)
    vakiot: set[int] = field(default_factory=set)  # osoitevakiot


def tutki(kuva: Kuva, alku: int, alue: tuple[int, int],
          eipaluuta: set[int] | None = None) -> Funktio:
    """Rekursiivinen läpikäynti yhden funktion sisällä: seurataan
    haaroja ja kerätään bl-kutsujen kohteet. Kutsu funktioon, joka ei
    palaa (eipaluuta), päättää lohkon."""
    eipaluuta = eipaluuta or set()
    funktio = Funktio(alku)
    jono, nahty = [alku], set[int]()
    movw: dict[str, int] = {}
    vertailu: dict[str, int] = {}     # viimeisin cmp rX, #n
    while jono:
        osoite = jono.pop()
        while alue[0] <= osoite < alue[1] and osoite not in nahty:
            kaskyt = pura(kuva, osoite, 1)
            if not kaskyt:
                break
            k = kaskyt[0]
            nahty.add(osoite)
            funktio.kaskyja += 1
            funktio.loppu = max(funktio.loppu, k.osoite + k.koko)
            ehdoton = k.nimi in ("b", "b.w")
            _vakio(kuva, k, funktio, movw)
            if k.nimi == "bl" and k.kohde is not None:
                funktio.kutsuu.add(k.kohde)
                if k.kohde in eipaluuta:
                    break
            elif _haara(k.nimi) and k.kohde is not None:
                if k.kohde < alku:
                    funktio.kutsuu.add(k.kohde)   # häntäkutsu
                    funktio.palautuu = True
                elif k.kohde < alue[1]:
                    jono.append(k.kohde)
            if paluu(k):
                funktio.palautuu = True
                break
            if k.nimi == "cmp" and "#" in k.operandit:
                rekisteri, luku = k.operandit.split(", #")
                vertailu[rekisteri] = int(luku, 0)
            if k.nimi == "tbb":
                kohteet = _hyppytaulu(kuva, k, vertailu)
                funktio.hyppytaulut[k.osoite] = kohteet
                jono.extend(kohteet)
                break
            if ehdoton or k.nimi.startswith(("tbh", "udf")):
                break
            osoite += k.koko
    return funktio


# @alku hyppytaulu
def _hyppytaulu(kuva: Kuva, k: Kasky, vertailu: dict[str, int]
                ) -> list[int]:
    """tbb [pc, rX]: taulukko alkaa heti käskyn jälkeen, ja jokainen
    tavu on hypyn pituus puolisanoina. Alkioiden määrä on yhtä suurempi
    kuin edeltävän cmp rX, #n -käskyn raja (sitä seuraa bhi oletukseen).
    """
    indeksi = k.operandit.rstrip("]").split(", ")[-1]
    maara = vertailu.get(indeksi, 0) + 1
    taulu = k.osoite + 4
    return [taulu + 2 * t for t in kuva.tavut(taulu, maara)]
# @loppu hyppytaulu


def _vakio(kuva: Kuva, k: Kasky, funktio: Funktio,
           movw: dict[str, int]) -> None:
    """Kerää käskyn lataaman vakion: literaalivarannon sanan tai
    mov.w-, movw- ja movt-käskyjen välittömän arvon."""
    rekisteri = k.operandit.split(",")[0]
    if k.lukee_pc and k.kohde is not None and kuva.sisaltaa(k.kohde, 4):
        funktio.vakiot.add(kuva.u32(k.kohde))
    elif k.vakio is not None and k.nimi == "movw":
        movw[rekisteri] = k.vakio
        funktio.vakiot.add(k.vakio)
    elif k.vakio is not None and k.nimi == "movt" and rekisteri in movw:
        funktio.vakiot.discard(movw[rekisteri])
        funktio.vakiot.add(k.vakio << 16 | movw.pop(rekisteri))
    elif k.vakio is not None and k.nimi == "mov.w":
        funktio.vakiot.add(k.vakio)


def etsi_funktiot(kuva: Kuva, juuret: list[int],
                  alue: tuple[int, int]) -> dict[int, Funktio]:
    """Kaikki funktiot, jotka löytyvät juurista bl-kutsuja seuraamalla.
    Juuret ovat esim. vektoritaulun osoitteet (ilman Thumb-bittiä).
    Läpikäynti toistetaan, kunnes palaamattomien funktioiden joukko
    (esim. lopeta) ei enää muutu."""
    eipaluuta: set[int] = set()
    while True:
        funktiot: dict[int, Funktio] = {}
        jono = list(juuret)
        while jono:
            osoite = jono.pop()
            if osoite in funktiot or not alue[0] <= osoite < alue[1]:
                continue
            f = tutki(kuva, osoite, alue, eipaluuta)
            funktiot[osoite] = f
            jono.extend(f.kutsuu)
        uudet = {o for o, f in funktiot.items() if not f.palautuu}
        if uudet == eipaluuta:
            return funktiot
        eipaluuta = uudet


def vektorijuuret(kuva: Kuva, taulu: int, maara: int) -> list[int]:
    """Vektoritaulun käsittelijät ilman Thumb-bittiä (sana 0 on pino)."""
    return sorted({kuva.u32(taulu + 4 * i) & ~1 for i in range(1, maara)
                   if kuva.u32(taulu + 4 * i)})


def kaikki_funktiot(kuva: Kuva, taulu: int, maara: int,
                    alue: tuple[int, int]) -> dict[int, Funktio]:
    """Funktiot vektoritaulusta ja datan funktio-osoittimista."""
    juuret = vektorijuuret(kuva, taulu, maara)
    juuret += osoitinjuuret(kuva, alue)
    return etsi_funktiot(kuva, sorted(set(juuret)), alue)


def osoitinjuuret(kuva: Kuva, alue: tuple[int, int]) -> list[int]:
    """Datan sanat, jotka näyttävät Thumb-funktio-osoittimilta: pariton
    arvo koodialueella. Näin löytyvät funktiot, joita kutsutaan vain
    epäsuorasti (komento- ja tehtävätaulut, takaisinkutsut). Pariton
    osoite voi olla myös merkkijonon alku, joten ne ohitetaan."""
    juuret = set()
    for _, arvo in kuva.sanat(alue[0], alue[1]):
        if not (arvo & 1 and alue[0] <= arvo - 1 < alue[1]):
            continue
        teksti = kuva.merkkijono(arvo)
        if teksti is None or len(teksti) < 2:
            juuret.add(arvo - 1)
    return sorted(juuret)
