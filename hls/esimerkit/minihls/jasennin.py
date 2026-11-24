"""Etupää: esikäsittely, sanastoanalyysi ja rekursiivisesti etenevä
jäsennin. Tulos on puu.Funktio."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .puu import (Binaari, Ehto, Funktio, Indeksi, Jos, KaannosVirhe,
                  Kirjoita, Lause, Lauseke, Lue, Luku, Nimi, Palauta,
                  Parametri, Pragma, Sijoitus, Silmukka, Unaari)


@dataclass(frozen=True)
class Merkki:
    laji: str                       # nimi, luku, op, pragma tai loppu
    teksti: str
    rivi: int


# @alku sanasto
SANASTO = re.compile(r"""
    (?P<tyhja>\s+|//[^\n]*|/\*.*?\*/)
  | (?P<luku>0[xX][0-9a-fA-F]+|\d+)
  | (?P<nimi>[A-Za-z_]\w*)
  | (?P<op><<=|>>=|<<|>>|<=|>=|==|!=|&&|\|\||\+\+|--|[-+*&|^]=
            |[-+*/%&|^~!<>=?:;,.()\[\]{}])
""", re.VERBOSE | re.DOTALL)


def sanat(lahde: str) -> list[Merkki]:
    """Pilkkoo lähteen merkeiksi. Esikäsittelijän rivit käsitellään
    tässä: #include ohitetaan, #define on yksinkertainen vakiomakro ja
    #pragma HLS välitetään jäsentimelle omana merkkinään."""
    makrot: dict[str, list[Merkki]] = {}
    tulos: list[Merkki] = []
    for rivi, teksti in enumerate(lahde.splitlines(), start=1):
        alku = teksti.strip()
        if alku.startswith("#pragma HLS"):
            tulos.append(Merkki("pragma", alku[len("#pragma HLS"):], rivi))
            continue
        if alku.startswith("#define"):
            osat = alku.split(maxsplit=2)
            makrot[osat[1]] = pilko(osat[2], rivi, makrot)
            continue
        if alku.startswith("#"):
            continue
        tulos.extend(pilko(teksti, rivi, makrot))
    tulos.append(Merkki("loppu", "", len(lahde.splitlines()) + 1))
    return tulos
# @loppu sanasto


def pilko(teksti: str, rivi: int,
          makrot: dict[str, list[Merkki]]) -> list[Merkki]:
    tulos: list[Merkki] = []
    kohta = 0
    while kohta < len(teksti):
        osuma = SANASTO.match(teksti, kohta)
        if osuma is None:
            raise KaannosVirhe(rivi, f"tuntematon merkki {teksti[kohta]!r}")
        kohta = osuma.end()
        laji = osuma.lastgroup
        assert laji is not None
        if laji == "tyhja":
            continue
        sana = osuma.group()
        if laji == "nimi" and sana in makrot:
            tulos.extend(Merkki(m.laji, m.teksti, rivi)
                         for m in makrot[sana])
        else:
            tulos.append(Merkki(laji, sana, rivi))
    return tulos


def lue_pragma(merkki: Merkki) -> Pragma:
    """'pipeline II=1' -> Pragma('pipeline', {'II': '1'})."""
    sanat_ = merkki.teksti.split()
    if not sanat_:
        raise KaannosVirhe(merkki.rivi, "tyhjä pragma")
    asetukset: dict[str, str] = {}
    for sana in sanat_[1:]:
        avain, _, arvo = sana.partition("=")
        asetukset[avain] = arvo
    return Pragma(sanat_[0].lower(), asetukset, merkki.rivi)


SILMUKAN_PRAGMAT = {"pipeline", "unroll"}

# Binäärioperaattorien sitovuus: suurempi sitoo tiukemmin.
SITOVUUS = {
    "||": 1, "&&": 2, "|": 3, "^": 4, "&": 5, "==": 6, "!=": 6,
    "<": 7, "<=": 7, ">": 7, ">=": 7, "<<": 8, ">>": 8,
    "+": 9, "-": 9, "*": 10, "/": 10, "%": 10,
}


class Jasennin:
    def __init__(self, merkit: list[Merkki]) -> None:
        self.merkit = merkit
        self.kohta = 0
        self.funktion_pragmat: list[Pragma] = []
        self.paikalliset: dict[str, int] = {}
        self.vakiotaulut: dict[str, list[int]] = {}
        self.silmukoita = 0

    # --- apufunktiot -------------------------------------------------
    @property
    def nyt(self) -> Merkki:
        return self.merkit[self.kohta]

    def katso(self, siirto: int = 1) -> Merkki:
        return self.merkit[min(self.kohta + siirto, len(self.merkit) - 1)]

    def ota(self) -> Merkki:
        merkki = self.nyt
        self.kohta += 1
        return merkki

    def on(self, teksti: str) -> bool:
        return self.nyt.teksti == teksti and self.nyt.laji != "pragma"

    def odota(self, teksti: str) -> Merkki:
        if not self.on(teksti):
            raise KaannosVirhe(self.nyt.rivi, f"odotettiin '{teksti}', "
                               f"saatiin '{self.nyt.teksti}'")
        return self.ota()

    def nimi(self) -> str:
        if self.nyt.laji != "nimi":
            raise KaannosVirhe(self.nyt.rivi, "odotettiin nimeä, saatiin "
                               f"'{self.nyt.teksti}'")
        return self.ota().teksti

    def vakio(self) -> int:
        rivi = self.nyt.rivi
        return vakioarvo(self.lauseke(), rivi)

    # --- funktio ja parametrit -------------------------------------------
    # @alku funktio
    def funktiot(self) -> list[Funktio]:
        tulos = []
        while self.nyt.laji != "loppu":
            tulos.append(self.funktio())
        return tulos

    def funktio(self) -> Funktio:
        palauttaa = self.ota().teksti == "int"
        nimi = self.nimi()
        self.odota("(")
        parametrit = [self.parametri()]
        while self.on(","):
            self.ota()
            parametrit.append(self.parametri())
        self.odota(")")
        self.funktion_pragmat, self.paikalliset = [], {}
        self.vakiotaulut = {}
        runko = self.lohko(silmukan_pragmat=None)
        return Funktio(nimi, palauttaa, parametrit, runko,
                       self.funktion_pragmat, self.paikalliset,
                       self.vakiotaulut)

    def parametri(self) -> Parametri:
        if self.on("virta"):              # virta<int>& x
            for odotettu in ("virta", "<", "int", ">", "&"):
                self.odota(odotettu)
            return Parametri(self.nimi(), "virta")
        vain_luku = self.on("const")
        if vain_luku:
            self.ota()
        rivi = self.odota("int").rivi
        if self.on("*") or self.on("&"):
            raise KaannosVirhe(rivi, "osoitin ei ole tuettu: käytä taulukkoa")
        nimi = self.nimi()
        if not self.on("["):
            return Parametri(nimi, "skalaari")
        self.ota()
        koko = self.vakio()
        self.odota("]")
        return Parametri(nimi, "taulu", koko, vain_luku)
    # @loppu funktio

    # --- lauseet -----------------------------------------------------
    def lohko(self, silmukan_pragmat: list[Pragma] | None) -> list[Lause]:
        if not self.on("{"):
            return self.lause(silmukan_pragmat)
        self.ota()
        lauseet: list[Lause] = []
        while not self.on("}"):
            lauseet.extend(self.lause(silmukan_pragmat))
        self.ota()
        return lauseet

    def lause(self, silmukan_pragmat: list[Pragma] | None) -> list[Lause]:
        merkki = self.nyt
        if merkki.laji == "pragma":
            self.ota()
            pragma = lue_pragma(merkki)
            if pragma.laji in SILMUKAN_PRAGMAT:
                if silmukan_pragmat is None:
                    raise KaannosVirhe(merkki.rivi, f"{pragma.laji} kuuluu "
                                       "silmukan runkoon")
                silmukan_pragmat.append(pragma)
            else:
                self.funktion_pragmat.append(pragma)
            return []
        if merkki.teksti in ("while", "do", "goto", "switch", "break"):
            raise KaannosVirhe(merkki.rivi, f"{merkki.teksti} ei ole tuettu "
                               "(ohjausvuon oltava vakio)")
        if self.on("int") or self.on("const"):
            return self.maarittely()
        if self.on("for"):
            return [self.silmukka(None)]
        if merkki.laji == "nimi" and self.katso().teksti == ":":
            self.ota()
            self.ota()
            return [self.silmukka(merkki.teksti)]
        if self.on("if"):
            return [self.jos()]
        if self.on("return"):
            self.ota()
            arvo = self.lauseke()
            self.odota(";")
            return [Palauta(arvo, merkki.rivi)]
        if merkki.laji == "nimi" and self.katso().teksti == ".":
            virta = self.nimi()
            self.odota(".")
            self.odota("write")
            self.odota("(")
            arvo = self.lauseke()
            self.odota(")")
            self.odota(";")
            return [Kirjoita(virta, arvo, merkki.rivi)]
        lause = self.sijoitus()
        self.odota(";")
        return [lause]

    def maarittely(self) -> list[Lause]:
        if self.on("const"):
            self.ota()
        rivi = self.odota("int").rivi
        nimi = self.nimi()
        if self.on("["):
            self.ota()
            koko = self.vakio()
            self.odota("]")
            if self.on("="):                    # vakiotaulukko
                self.ota()
                self.odota("{")
                arvot = [self.vakio()]
                while self.on(","):
                    self.ota()
                    arvot.append(self.vakio())
                self.odota("}")
                if len(arvot) != koko:
                    raise KaannosVirhe(rivi, f"{nimi}: {len(arvot)} arvoa, "
                                       f"odotettiin {koko}")
                self.vakiotaulut[nimi] = arvot
            else:
                self.paikalliset[nimi] = koko
            self.odota(";")
            return []
        lauseet: list[Lause] = []
        if self.on("="):
            self.ota()
            lauseet.append(Sijoitus(Nimi(nimi), self.lauseke(), rivi))
        self.odota(";")
        return lauseet

    # @alku sijoitus
    def sijoitus(self) -> Sijoitus:
        rivi = self.nyt.rivi
        kohde = self.kohde()
        op = self.ota().teksti
        if op in ("++", "--"):
            return Sijoitus(kohde, Binaari(op[0], kohde, Luku(1)), rivi)
        if op == "=":
            return Sijoitus(kohde, self.lauseke(), rivi)
        if len(op) >= 2 and op.endswith("="):    # += -= <<= ...
            return Sijoitus(kohde, Binaari(op[:-1], kohde,
                                           self.lauseke()), rivi)
        raise KaannosVirhe(rivi, f"odotettiin sijoitusta, saatiin '{op}'")
    # @loppu sijoitus

    def kohde(self) -> Nimi | Indeksi:
        nimi = self.nimi()
        if not self.on("["):
            return Nimi(nimi)
        self.ota()
        indeksi = self.lauseke()
        self.odota("]")
        return Indeksi(nimi, indeksi)

    def jos(self) -> Jos:
        rivi = self.odota("if").rivi
        self.odota("(")
        ehto = self.lauseke()
        self.odota(")")
        tosi = self.lohko(None)
        epatosi: list[Lause] = []
        if self.on("else"):
            self.ota()
            epatosi = self.lohko(None)
        return Jos(ehto, tosi, epatosi, rivi)

    # @alku silmukka
    def silmukka(self, nimi: str | None) -> Silmukka:
        rivi = self.odota("for").rivi
        self.odota("(")
        self.odota("int")
        muuttuja = self.nimi()
        self.odota("=")
        alku = self.vakio()
        self.odota(";")
        if self.nimi() != muuttuja:
            raise KaannosVirhe(rivi, "ehdon on koskettava silmukkamuuttujaa")
        vertailu = self.ota().teksti
        raja = self.vakio()
        self.odota(";")
        askel = self.askel(muuttuja, rivi)
        self.odota(")")
        pragmat: list[Pragma] = []
        runko = self.lohko(pragmat)
        kierrokset = kierrosmaara(alku, vertailu, raja, askel, rivi)
        self.silmukoita += 1
        return Silmukka(nimi or f"silmukka{self.silmukoita}", muuttuja,
                        alku, askel, kierrokset, runko, pragmat, rivi)
    # @loppu silmukka

    def askel(self, muuttuja: str, rivi: int) -> int:
        if self.on("++") or self.on("--"):
            suunta = self.ota().teksti
            self.odota(muuttuja)
            return 1 if suunta == "++" else -1
        if self.nimi() != muuttuja:
            raise KaannosVirhe(rivi, "askeleen on muutettava muuttujaa")
        op = self.ota().teksti
        if op in ("++", "--"):
            return 1 if op == "++" else -1
        if op in ("+=", "-="):
            maara = self.vakio()
            return maara if op == "+=" else -maara
        raise KaannosVirhe(rivi, f"tuntematon silmukan askel '{op}'")

    # --- lausekkeet ----------------------------------------------------
    # @alku lauseke
    def lauseke(self) -> Lauseke:
        ehto = self.binaari(1)
        if not self.on("?"):
            return ehto
        self.ota()
        tosi = self.lauseke()
        self.odota(":")
        return Ehto(ehto, tosi, self.lauseke())

    def binaari(self, vahintaan: int) -> Lauseke:
        """Operaattorin sitovuuteen perustuva jäsennys: vasen operandi
        jäsennetään ensin, ja tiukemmin sitovat operaattorit kootaan
        rekursiossa oikeaksi operandiksi."""
        vasen = self.unaari()
        while (self.nyt.laji == "op" and
               SITOVUUS.get(self.nyt.teksti, 0) >= vahintaan):
            op = self.ota().teksti
            oikea = self.binaari(SITOVUUS[op] + 1)
            vasen = Binaari(op, vasen, oikea)
        return vasen

    def unaari(self) -> Lauseke:
        if self.nyt.teksti in ("-", "~", "!"):
            return Unaari(self.ota().teksti, self.unaari())
        return self.perus()

    def perus(self) -> Lauseke:
        merkki = self.ota()
        if merkki.laji == "luku":
            return Luku(int(merkki.teksti, 0))
        if merkki.teksti == "(":
            arvo = self.lauseke()
            self.odota(")")
            return arvo
        if merkki.laji != "nimi":
            raise KaannosVirhe(merkki.rivi, "odotettiin lauseketta, saatiin "
                               f"'{merkki.teksti}'")
        if self.on("["):
            self.ota()
            indeksi = self.lauseke()
            self.odota("]")
            return Indeksi(merkki.teksti, indeksi)
        if self.on("."):
            self.ota()
            self.odota("read")
            self.odota("(")
            self.odota(")")
            return Lue(merkki.teksti)
        return Nimi(merkki.teksti)
    # @loppu lauseke


def vakioarvo(lauseke: Lauseke, rivi: int) -> int:
    """Laskee vakiolausekkeen arvon, esim. taulukon koon N - 1."""
    match lauseke:
        case Luku(arvo):
            return arvo
        case Unaari("-", arvo):
            return -vakioarvo(arvo, rivi)
        case Binaari(op, vasen, oikea):
            a, b = vakioarvo(vasen, rivi), vakioarvo(oikea, rivi)
            laskut = {"+": a + b, "-": a - b, "*": a * b,
                      "<<": a << b if b >= 0 else 0, ">>": a >> max(b, 0)}
            if op in laskut:
                return laskut[op]
    raise KaannosVirhe(rivi, "odotettiin käännösaikaista vakiota")


def kierrosmaara(alku: int, vertailu: str, raja: int, askel: int,
                 rivi: int) -> int:
    if askel == 0:
        raise KaannosVirhe(rivi, "silmukan askel on nolla")
    if vertailu in ("<=", ">="):
        raja += 1 if vertailu == "<=" else -1
    if vertailu in ("<", "<=") and askel > 0:
        maara = (raja - alku + askel - 1) // askel
    elif vertailu in (">", ">=") and askel < 0:
        maara = (alku - raja - askel - 1) // -askel
    else:
        raise KaannosVirhe(rivi, "silmukan ehto ja askel eivät sovi yhteen")
    if maara < 1:
        raise KaannosVirhe(rivi, "silmukka ei suorita yhtään kierrosta")
    return maara


def jasenna(lahde: str) -> list[Funktio]:
    return Jasennin(sanat(lahde)).funktiot()
