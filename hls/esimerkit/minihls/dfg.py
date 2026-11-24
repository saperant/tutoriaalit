"""Välikieli: tietovuograafi (dataflow graph) yhdelle alueelle.

Suoraviivainen koodi muutetaan graafiksi, jonka solmut ovat
operaatioita ja kaaret datariippuvuuksia. Muuttujan sijoitus ei tuota
solmua: nimi vain sidotaan uuteen arvoon (SSA-muoto). Ehtolauseet
muutetaan valinnoiksi (if-conversion), ja muistioperaatioiden väliset
riippuvuudet lisätään järjestyskaariksi.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .muunnokset import Lehti
from .puu import (Binaari, Ehto, Funktio, Indeksi, Jos, KaannosVirhe,
                  Kirjoita, Lause, Lauseke, Lue, Luku, Nimi, Palauta,
                  Sijoitus, Silmukka, Unaari)


# @alku operandit
@dataclass(frozen=True)
class Vakio:
    arvo: int


@dataclass(frozen=True)
class Vakaa:
    """Alueen aikana muuttumaton signaali: skalaariparametri tai
    ulomman silmukan laskuri."""
    nimi: str


@dataclass(frozen=True)
class Viite:
    solmu: int


Operandi = Vakio | Vakaa | Viite
# @loppu operandit


@dataclass(frozen=True)
class Affiini:
    """Indeksi muodossa vakio + summa(kerroin * n), missä n on silmukan
    kierrosnumero 0, 1, 2, ..."""
    vakio: int
    kertoimet: tuple[tuple[str, int], ...] = ()

    def kerroin(self, silmukka: str) -> int:
        return dict(self.kertoimet).get(silmukka, 0)


# @alku solmu
@dataclass
class Solmu:
    id: int
    laji: str                   # +, *, lataa, tallenna, kirjoita, ...
    syotteet: list[Operandi]
    leveys: int = 32
    kohde: str = ""             # muuttuja, taulukko tai virta
    pankki: int = 0
    ehto: Operandi | None = None
    affiini: Affiini | None = None
    pankkeja: int = 1
    rivi: int = 0

    @property
    def muisti(self) -> str:
        """Muistipankin nimi: a tai jaetun taulukon pankki a_1."""
        if self.pankkeja == 1:
            return self.kohde
        return f"{self.kohde}_{self.pankki}"


@dataclass(frozen=True)
class Reuna:
    """Järjestysehto: kohde aikaisintaan jaksolla lahto + viive."""
    lahto: int
    kohde: int
    viive: int


@dataclass(frozen=True)
class Kantava:
    """Silmukan kantama riippuvuus: kierroksen n solmu lahto ja kierroksen
    n + etaisyys solmu kohde. Ehto: kohde + II * etaisyys >= lahto +
    viive."""
    lahto: int
    kohde: int
    viive: int
    etaisyys: int
    syy: str


@dataclass
class Dfg:
    solmut: dict[int, Solmu] = field(default_factory=dict)
    reunat: list[Reuna] = field(default_factory=list)
    kantavat: list[Kantava] = field(default_factory=list)
# @loppu solmu

    def kayttajat(self) -> dict[int, list[int]]:
        tulos: dict[int, list[int]] = {i: [] for i in self.solmut}
        for s in self.solmut.values():
            for o in operandit(s):
                if isinstance(o, Viite):
                    tulos[o.solmu].append(s.id)
        return tulos


def operandit(solmu: Solmu) -> list[Operandi]:
    if solmu.ehto is None:
        return list(solmu.syotteet)
    return [*solmu.syotteet, solmu.ehto]


SIVUVAIKUTUKSET = {"tallenna", "kirjoita", "kirjoita_virta", "palauta",
                   "lue_virta"}
VERTAILUT = {"<", "<=", ">", ">=", "==", "!="}


@dataclass(frozen=True)
class Jako:
    laji: str                   # none, cyclic, block tai complete
    tekija: int = 1


@dataclass(frozen=True)
class Silmukkatieto:
    nimi: str
    muuttuja: str
    alku: int
    askel: int
    kierrokset: int


def kaksikanta(arvo: int, rivi: int, mika: str) -> int:
    if arvo < 1 or arvo & (arvo - 1):
        raise KaannosVirhe(rivi, f"{mika} {arvo} ei ole kahden potenssi")
    return arvo.bit_length() - 1


def rajaa(arvo: int) -> int:
    """32-bittinen kahden komplementin kierto."""
    arvo &= 0xFFFFFFFF
    return arvo - (1 << 32) if arvo & 0x80000000 else arvo


class Rakentaja:
    """Rakentaa yhden lehden tietovuograafin."""

    def __init__(self, funktio: Funktio, lehti: Lehti,
                 ulommat: list[Silmukkatieto], jaot: dict[str, Jako],
                 riippumattomat: dict[str, int | None],
                 alku: int = 0) -> None:
        self.f = funktio
        self.lehti = lehti
        self.ulommat = {u.muuttuja: u for u in ulommat}
        self.jaot = jaot
        self.riippumattomat = riippumattomat
        self.g = Dfg()
        self.seuraava = alku
        self.ymparisto: dict[str, Operandi] = {}
        self.luetut: dict[str, int] = {}
        self.iteraatio: int | None = None
        self.yhteiset: dict[tuple[object, ...], int] = {}
        self.muisti: dict[tuple[str, int], list[int]] = {}
        self.virrat: dict[str, list[int]] = {}
        self.affiinit: dict[Operandi, Affiini | None] = {}

    # --- solmujen luonti ------------------------------------------------
    def uusi(self, laji: str, syotteet: list[Operandi], rivi: int,
             leveys: int = 32, **tiedot: object) -> int:
        solmu = Solmu(self.seuraava, laji, syotteet, leveys, rivi=rivi)
        for avain, arvo in tiedot.items():
            setattr(solmu, avain, arvo)
        self.g.solmut[solmu.id] = solmu
        self.seuraava += 1
        return solmu.id

    def leveys(self, o: Operandi) -> int:
        if isinstance(o, Viite):
            return self.g.solmut[o.solmu].leveys
        return 32

    # @alku op
    def op(self, laji: str, a: Operandi, b: Operandi, rivi: int) -> Operandi:
        """Binäärioperaatio vakioiden laskostuksella, yksinkertaistuksilla
        ja yhteisten alilausekkeiden poistolla."""
        if laji in ("&&", "||"):
            a, b = self.totuus(a, rivi), self.totuus(b, rivi)
            laji = "&" if laji == "&&" else "|"
        elif laji not in VERTAILUT and (self.leveys(a) == 1) != (
                self.leveys(b) == 1):
            a, b = self.laajenna(a, rivi), self.laajenna(b, rivi)
        if isinstance(a, Vakio) and isinstance(b, Vakio):
            return Vakio(laske(laji, a.arvo, b.arvo))
        if laji in ("+", "*", "&", "|", "^", "==", "!=") and \
                isinstance(a, Vakio):
            a, b = b, a                     # vakio oikealle
        if isinstance(b, Vakio):
            if b.arvo == 0 and laji in ("+", "-", "|", "^", "<<", ">>"):
                return a
            if b.arvo == 0 and laji in ("*", "&"):
                return Vakio(0)
            if b.arvo == 1 and laji == "*":
                return a
            if laji == "*" and b.arvo > 0 and b.arvo & (b.arvo - 1) == 0:
                laji, b = "<<", Vakio(b.arvo.bit_length() - 1)
        avain = (laji, a, b)
        if avain not in self.yhteiset:
            leveys = 1 if laji in VERTAILUT or self.leveys(a) == 1 else 32
            self.yhteiset[avain] = self.uusi(laji, [a, b], rivi, leveys)
        return Viite(self.yhteiset[avain])
    # @loppu op

    def unaari(self, laji: str, a: Operandi, rivi: int) -> Operandi:
        if laji == "-":
            return self.op("-", Vakio(0), self.laajenna(a, rivi), rivi)
        if laji == "!":
            return self.op("==", self.totuus(a, rivi), Vakio(0), rivi)
        if isinstance(a, Vakio):
            return Vakio(rajaa(~a.arvo))
        return Viite(self.uusi("~", [a], rivi, self.leveys(a)))

    def totuus(self, a: Operandi, rivi: int) -> Operandi:
        if isinstance(a, Vakio):
            return Vakio(int(a.arvo != 0))
        if self.leveys(a) == 1:
            return a
        return self.op("!=", a, Vakio(0), rivi)

    def laajenna(self, a: Operandi, rivi: int) -> Operandi:
        if self.leveys(a) == 32:
            return a
        avain = ("laajenna", a)
        if avain not in self.yhteiset:
            self.yhteiset[avain] = self.uusi("laajenna", [a], rivi)
        return Viite(self.yhteiset[avain])

    def valinta(self, ehto: Operandi, a: Operandi, b: Operandi,
                rivi: int) -> Operandi:
        if a == b:
            return a
        if isinstance(ehto, Vakio):
            return a if ehto.arvo else b
        a, b = self.laajenna(a, rivi), self.laajenna(b, rivi)
        return Viite(self.uusi("valinta", [ehto, a, b], rivi))

    def ja(self, a: Operandi | None, b: Operandi, rivi: int) -> Operandi:
        return b if a is None else self.op("&", a, b, rivi)

    # --- nimet ja muuttujat ----------------------------------------------
    def nimen_arvo(self, nimi: str, rivi: int) -> Operandi:
        lehti = self.lehti
        if nimi == lehti.muuttuja and lehti.kierrokset > 1:
            if self.iteraatio is None:
                self.iteraatio = self.uusi("iteraatio", [], rivi)
                self.affiinit[Viite(self.iteraatio)] = Affiini(
                    lehti.alku, ((lehti.nimi, lehti.askel),))
            return Viite(self.iteraatio)
        if nimi == lehti.muuttuja:
            return Vakio(lehti.alku)
        if nimi in self.ulommat:
            u = self.ulommat[nimi]
            arvo = Vakaa(f"m_{nimi}")
            self.affiinit[arvo] = Affiini(u.alku, ((u.nimi, u.askel),))
            return arvo
        parametri = self.f.parametri(nimi)
        if parametri is not None:
            if parametri.laji != "skalaari":
                raise KaannosVirhe(rivi, f"{nimi} ei ole skalaari")
            return Vakaa(nimi)
        if nimi in self.ymparisto:
            return self.ymparisto[nimi]
        if nimi not in self.luetut:
            self.luetut[nimi] = self.uusi("muuttuja", [], rivi, kohde=nimi)
        return Viite(self.luetut[nimi])

    def affiini(self, o: Operandi) -> Affiini | None:
        if isinstance(o, Vakio):
            return Affiini(o.arvo)
        if o in self.affiinit:
            return self.affiinit[o]
        if not isinstance(o, Viite):
            return None
        s = self.g.solmut[o.solmu]
        if s.laji not in ("+", "-", "*", "<<") or len(s.syotteet) != 2:
            return None
        a, b = (self.affiini(x) for x in s.syotteet)
        if a is None or b is None:
            return None
        if s.laji in ("+", "-"):
            merkki = 1 if s.laji == "+" else -1
            k = dict(a.kertoimet)
            for nimi, c in b.kertoimet:
                k[nimi] = k.get(nimi, 0) + merkki * c
            return Affiini(a.vakio + merkki * b.vakio,
                           tuple(sorted((n, c) for n, c in k.items() if c)))
        if b.kertoimet:
            return None
        kerroin = b.vakio if s.laji == "*" else 1 << b.vakio
        return Affiini(a.vakio * kerroin,
                       tuple((n, c * kerroin) for n, c in a.kertoimet))

    # --- lausekkeet ----------------------------------------------------
    def lauseke(self, e: Lauseke, rivi: int) -> Operandi:
        match e:
            case Luku(arvo):
                return Vakio(rajaa(arvo))
            case Nimi(nimi):
                return self.nimen_arvo(nimi, rivi)
            case Indeksi(taulu, indeksi):
                return self.lataa(taulu, indeksi, rivi)
            case Binaari(op, vasen, oikea):
                if op in ("/", "%"):
                    raise KaannosVirhe(rivi, "jakolasku ei ole tuettu")
                return self.op(op, self.lauseke(vasen, rivi),
                               self.lauseke(oikea, rivi), rivi)
            case Unaari(op, arvo):
                return self.unaari(op, self.lauseke(arvo, rivi), rivi)
            case Ehto(ehto, tosi, epatosi):
                return self.valinta(self.totuus(self.lauseke(ehto, rivi),
                                                rivi),
                                    self.lauseke(tosi, rivi),
                                    self.lauseke(epatosi, rivi), rivi)
            case Lue(virta):
                self.tarkista_virta(virta, rivi)
                if self.predikaatti is not None:
                    raise KaannosVirhe(rivi, "ehdollinen virran luku ei "
                                       "ole tuettu")
                return Viite(self.virtaoperaatio("lue_virta", virta, [],
                                                 rivi))

    def tarkista_virta(self, virta: str, rivi: int) -> None:
        p = self.f.parametri(virta)
        if p is None or p.laji != "virta":
            raise KaannosVirhe(rivi, f"{virta} ei ole virta")

    def virtaoperaatio(self, laji: str, virta: str,
                       syotteet: list[Operandi], rivi: int) -> int:
        solmu = self.uusi(laji, syotteet, rivi, kohde=virta)
        edelliset = self.virrat.setdefault(virta, [])
        if edelliset:
            self.g.reunat.append(Reuna(edelliset[-1], solmu, 1))
        edelliset.append(solmu)
        return solmu

    # @alku muisti
    def osoite(self, taulu: str, indeksi: Lauseke,
               rivi: int) -> tuple[int, int, Operandi, Affiini | None]:
        """Palauttaa pankkien määrän, pankin, pankin sisäisen osoitteen
        ja indeksin affiinin muodon."""
        tieto = self.muistitaulu(taulu)
        assert tieto is not None
        koko = tieto[0]
        arvo = self.lauseke(indeksi, rivi)
        if isinstance(arvo, Vakio) and not 0 <= arvo.arvo < koko:
            raise KaannosVirhe(rivi, f"indeksi {arvo.arvo} on taulukon "
                               f"{taulu} ulkopuolella")
        a = self.affiini(arvo)
        jako = self.jaot.get(taulu, Jako("none"))
        if jako.laji == "none":
            return 1, 0, arvo, a
        bitit = kaksikanta(jako.tekija, rivi, "jakokerroin")
        if jako.laji == "cyclic":
            pankki = None
            if a is not None and all(c % jako.tekija == 0
                                     for _, c in a.kertoimet):
                pankki = a.vakio % jako.tekija
            paikka = self.op(">>", arvo, Vakio(bitit), rivi)
        else:
            koko //= jako.tekija
            kaksikanta(koko, rivi, "pankin koko")
            pankki = self.lohkon_pankki(a, koko)
            paikka = self.op("&", arvo, Vakio(koko - 1), rivi)
        if pankki is None:
            raise KaannosVirhe(rivi, f"taulukon {taulu} pankki ei ole "
                               "vakio")
        return jako.tekija, pankki, paikka, a
    # @loppu muisti

    def muistitaulu(self, nimi: str) -> tuple[int, bool] | None:
        """(koko, vain luku), jos nimi on muistiin sijoitettava taulukko:
        parametri tai paikallinen taulukko, jota ei ole jaettu
        rekistereiksi."""
        p = self.f.parametri(nimi)
        if p is not None and p.laji == "taulu":
            return p.koko, p.vain_luku
        if nimi in self.f.paikalliset and not self.rekistereina(nimi):
            return self.f.paikalliset[nimi], False
        return None

    def rekistereina(self, nimi: str) -> bool:
        return nimi in self.f.paikalliset and \
            self.jaot.get(nimi, Jako("none")).laji == "complete"

    def lohkon_pankki(self, a: Affiini | None, koko: int) -> int | None:
        if a is None:
            return None
        pienin = suurin = a.vakio
        for nimi, c in a.kertoimet:
            n = self.kierroksia(nimi) - 1
            pienin += min(0, c * n)
            suurin += max(0, c * n)
        return pienin // koko if pienin // koko == suurin // koko else None

    def kierroksia(self, silmukka: str) -> int:
        if silmukka == self.lehti.nimi:
            return self.lehti.kierrokset
        return next(u.kierrokset for u in self.ulommat.values()
                    if u.nimi == silmukka)

    def paikallinen(self, taulu: str, indeksi: Lauseke, rivi: int) -> str:
        arvo = self.lauseke(indeksi, rivi)
        if not isinstance(arvo, Vakio):
            raise KaannosVirhe(rivi, f"paikallisen taulukon {taulu} "
                               "indeksin on oltava vakio (avaa silmukka)")
        if not 0 <= arvo.arvo < self.f.paikalliset[taulu]:
            raise KaannosVirhe(rivi, f"indeksi {arvo.arvo} on taulukon "
                               f"{taulu} ulkopuolella")
        return f"{taulu}[{arvo.arvo}]"

    def lataa(self, taulu: str, indeksi: Lauseke, rivi: int) -> Operandi:
        if taulu in self.f.vakiotaulut:
            arvo = self.lauseke(indeksi, rivi)
            arvot = self.f.vakiotaulut[taulu]
            if not isinstance(arvo, Vakio) or not 0 <= arvo.arvo < len(arvot):
                raise KaannosVirhe(rivi, f"vakiotaulukon {taulu} indeksin "
                                   "on oltava vakio (avaa silmukka)")
            return Vakio(rajaa(arvot[arvo.arvo]))
        if self.rekistereina(taulu):
            return self.nimen_arvo(self.paikallinen(taulu, indeksi, rivi),
                                   rivi)
        if self.muistitaulu(taulu) is None:
            raise KaannosVirhe(rivi, f"{taulu} ei ole taulukko")
        pankkeja, pankki, paikka, a = self.osoite(taulu, indeksi, rivi)
        avain = ("lataa", taulu, pankki, paikka)
        if avain in self.yhteiset:
            return Viite(self.yhteiset[avain])
        solmu = self.uusi("lataa", [paikka], rivi, kohde=taulu,
                          pankki=pankki, affiini=a, pankkeja=pankkeja)
        self.muistijarjestys(taulu, pankki, solmu)
        self.yhteiset[avain] = solmu
        return Viite(solmu)

    def muistijarjestys(self, taulu: str, pankki: int, uusi: int) -> None:
        """Järjestyskaaret saman muistipankin aiempiin operaatioihin,
        jos osoitteet voivat olla samat."""
        s = self.g.solmut[uusi]
        edelliset = self.muisti.setdefault((taulu, pankki), [])
        for e in edelliset:
            aiempi = self.g.solmut[e]
            if "tallenna" not in (aiempi.laji, s.laji):
                continue
            if samassa_kierroksessa(aiempi.affiini, s.affiini):
                viive = 1 if aiempi.laji == "tallenna" else 0
                self.g.reunat.append(Reuna(e, uusi, viive))
        edelliset.append(uusi)

    # --- lauseet -------------------------------------------------------
    predikaatti: Operandi | None = None

    def lauseet(self, lauseet: list[Lause]) -> None:
        for lause in lauseet:
            self.lause(lause)

    def lause(self, lause: Lause) -> None:
        match lause:
            case Sijoitus(Nimi(nimi), arvo, rivi):
                if nimi == self.lehti.muuttuja or nimi in self.ulommat or \
                        self.f.parametri(nimi) is not None:
                    raise KaannosVirhe(rivi, f"{nimi}: sijoitus ei ole "
                                       "sallittu")
                self.ymparisto[nimi] = self.lauseke(arvo, rivi)
            case Sijoitus(Indeksi(taulu, indeksi), arvo, rivi):
                if self.rekistereina(taulu):
                    nimi = self.paikallinen(taulu, indeksi, rivi)
                    self.ymparisto[nimi] = self.lauseke(arvo, rivi)
                else:
                    self.tallenna(taulu, indeksi, arvo, rivi)
            case Kirjoita(virta, arvo, rivi):
                self.tarkista_virta(virta, rivi)
                if self.predikaatti is not None:
                    raise KaannosVirhe(rivi, "ehdollinen virran kirjoitus "
                                       "ei ole tuettu")
                self.virtaoperaatio("kirjoita_virta", virta,
                                    [self.laajenna(self.lauseke(arvo, rivi),
                                                   rivi)], rivi)
            case Palauta(arvo, rivi):
                self.uusi("palauta", [self.laajenna(
                    self.lauseke(arvo, rivi), rivi)], rivi)
            case Jos():
                self.jos(lause)
            case Silmukka(rivi=rivi):
                raise KaannosVirhe(rivi, "silmukka lehden sisällä")

    def tallenna(self, taulu: str, indeksi: Lauseke, arvo: Lauseke,
                 rivi: int) -> None:
        tieto = self.muistitaulu(taulu)
        if tieto is None:
            raise KaannosVirhe(rivi, f"{taulu} ei ole taulukko")
        if tieto[1]:
            raise KaannosVirhe(rivi, f"{taulu} on const")
        data = self.laajenna(self.lauseke(arvo, rivi), rivi)
        pankkeja, pankki, paikka, a = self.osoite(taulu, indeksi, rivi)
        solmu = self.uusi("tallenna", [paikka, data], rivi, kohde=taulu,
                          pankki=pankki, ehto=self.predikaatti, affiini=a,
                          pankkeja=pankkeja)
        self.muistijarjestys(taulu, pankki, solmu)
        for avain in [k for k in self.yhteiset if k[:2] == ("lataa", taulu)]:
            del self.yhteiset[avain]

    # @alku jos
    def jos(self, lause: Jos) -> None:
        """If-conversion: molemmat haarat lasketaan, muuttujien arvot
        yhdistetään valinnalla ja tallennukset saavat predikaatin."""
        ehto = self.totuus(self.lauseke(lause.ehto, lause.rivi), lause.rivi)
        ulompi, alku = self.predikaatti, dict(self.ymparisto)
        self.predikaatti = self.ja(ulompi, ehto, lause.rivi)
        self.lauseet(lause.tosi)
        tosi = self.ymparisto
        self.ymparisto = dict(alku)
        self.predikaatti = self.ja(
            ulompi, self.unaari("!", ehto, lause.rivi), lause.rivi)
        self.lauseet(lause.epatosi)
        epatosi = self.ymparisto
        self.predikaatti, self.ymparisto = ulompi, dict(alku)
        for nimi in sorted(set(tosi) | set(epatosi)):
            a = tosi.get(nimi) or self.nimen_arvo(nimi, lause.rivi)
            b = epatosi.get(nimi) or self.nimen_arvo(nimi, lause.rivi)
            self.ymparisto[nimi] = self.valinta(ehto, a, b, lause.rivi)
    # @loppu jos

    # --- lopetus -------------------------------------------------------
    def valmis(self, elavat: set[str]) -> Dfg:
        """Lisää muuttujien kirjoitukset, poistaa kuolleen koodin ja
        laskee silmukan kantamat riippuvuudet."""
        for nimi, arvo in sorted(self.ymparisto.items()):
            luku = self.luetut.get(nimi)
            if luku is not None and arvo == Viite(luku):
                continue
            if luku is None and nimi not in elavat and \
                    nimi.split("[")[0] not in elavat:
                continue
            solmu = self.uusi("kirjoita", [arvo], self.lehti_rivi(),
                              self.leveys(arvo), kohde=nimi)
            if luku is not None:
                self.g.reunat.append(Reuna(luku, solmu, 0))
                self.g.kantavat.append(Kantava(solmu, luku, 1, 1,
                                               f"muuttuja {nimi}"))
        poista_kuolleet(self.g)
        if self.lehti.kierrokset > 1:
            self.muistin_kantavat()
            self.virtojen_kantavat()
        return self.g

    def lehti_rivi(self) -> int:
        return max((s.rivi for s in self.g.solmut.values()), default=0)

    def muistin_kantavat(self) -> None:
        ryhmat: dict[tuple[str, int], list[Solmu]] = {}
        for s in self.g.solmut.values():
            if s.laji in ("lataa", "tallenna"):
                ryhmat.setdefault((s.kohde, s.pankki), []).append(s)
        for (taulu, _), solmut in sorted(ryhmat.items()):
            pakotettu = self.riippumattomat.get(taulu, 0)
            for a in solmut:
                for b in solmut:
                    if "tallenna" not in (a.laji, b.laji):
                        continue
                    if pakotettu is None:
                        continue           # dependence ... false
                    d = pakotettu or etaisyys(a.affiini, b.affiini,
                                              self.lehti)
                    if d is None:
                        continue
                    viive = 1 if a.laji == "tallenna" else 0
                    syy = f"taulukko {taulu} ({a.laji} -> {b.laji})"
                    self.g.kantavat.append(Kantava(a.id, b.id, viive, d,
                                                   syy))

    def virtojen_kantavat(self) -> None:
        for virta, solmut in sorted(self.virrat.items()):
            elossa = [s for s in solmut if s in self.g.solmut]
            if len(elossa) > 1:
                self.g.kantavat.append(Kantava(elossa[-1], elossa[0], 1, 1,
                                               f"virta {virta}"))


def laske(laji: str, a: int, b: int) -> int:
    tulokset = {
        "+": a + b, "-": a - b, "*": a * b, "&": a & b, "|": a | b,
        "^": a ^ b, "<<": a << (b & 31), ">>": a >> (b & 31),
        "<": int(a < b), "<=": int(a <= b), ">": int(a > b),
        ">=": int(a >= b), "==": int(a == b), "!=": int(a != b),
    }
    return rajaa(tulokset[laji])


def samassa_kierroksessa(a: Affiini | None, b: Affiini | None) -> bool:
    """Voivatko kaksi saman kierroksen osoitetta olla samat?"""
    if a is None or b is None or a.kertoimet != b.kertoimet:
        return True
    return a.vakio == b.vakio


# @alku etaisyys
def etaisyys(a: Affiini | None, b: Affiini | None,
             lehti: Lehti) -> int | None:
    """Pienin kierrosten etäisyys d >= 1, jolla kierroksen n osoite a ja
    kierroksen n + d osoite b voivat olla samat. None: ei koskaan."""
    if a is None or b is None:
        return 1                            # ei tiedetä: oletetaan pahin
    muut_a = [x for x in a.kertoimet if x[0] != lehti.nimi]
    muut_b = [x for x in b.kertoimet if x[0] != lehti.nimi]
    if muut_a != muut_b:
        return 1
    c, cb = a.kerroin(lehti.nimi), b.kerroin(lehti.nimi)
    if c != cb:
        return 1
    ero = a.vakio - b.vakio                 # c * n + a = c * (n + d) + b
    if c == 0:
        return 1 if ero == 0 else None
    if ero % c:
        return None
    d = ero // c
    return d if 1 <= d < lehti.kierrokset else None
# @loppu etaisyys


def poista_kuolleet(g: Dfg) -> None:
    muuttui = True
    while muuttui:
        kayttajat = g.kayttajat()
        kuolleet = [i for i, s in g.solmut.items()
                    if not kayttajat[i] and s.laji not in SIVUVAIKUTUKSET]
        muuttui = bool(kuolleet)
        for i in kuolleet:
            del g.solmut[i]
    g.reunat = [r for r in g.reunat
                if r.lahto in g.solmut and r.kohde in g.solmut]
    g.kantavat = [k for k in g.kantavat
                  if k.lahto in g.solmut and k.kohde in g.solmut]
