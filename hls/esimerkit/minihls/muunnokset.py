"""Puun muunnokset ennen tietovuograafia: silmukoiden avaaminen ja
funktion jakaminen alueiksi, joista kukin ajoitetaan erikseen."""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from .puu import (Binaari, Ehto, Indeksi, Jos, KaannosVirhe, Kirjoita,
                  Lause, Lauseke, Lue, Luku, Nimi, Palauta, Sijoitus,
                  Silmukka, Unaari)


def korvaa(lauseke: Lauseke, nimi: str, uusi: Lauseke) -> Lauseke:
    """Korvaa lausekkeesta muuttujan nimi lausekkeella uusi."""
    match lauseke:
        case Nimi(n) if n == nimi:
            return uusi
        case Indeksi(taulu, indeksi):
            return Indeksi(taulu, korvaa(indeksi, nimi, uusi))
        case Binaari(op, vasen, oikea):
            return Binaari(op, korvaa(vasen, nimi, uusi),
                           korvaa(oikea, nimi, uusi))
        case Unaari(op, arvo):
            return Unaari(op, korvaa(arvo, nimi, uusi))
        case Ehto(e, t, f):
            return Ehto(korvaa(e, nimi, uusi), korvaa(t, nimi, uusi),
                        korvaa(f, nimi, uusi))
        case _:
            return lauseke


def korvaa_lause(lause: Lause, nimi: str, uusi: Lauseke) -> Lause:
    match lause:
        case Sijoitus(kohde, arvo, rivi):
            if isinstance(kohde, Nimi) and kohde.nimi == nimi:
                raise KaannosVirhe(rivi, f"silmukkamuuttujaa {nimi} ei saa "
                                   "muuttaa rungossa")
            uusi_kohde = korvaa(kohde, nimi, uusi)
            assert isinstance(uusi_kohde, Nimi | Indeksi)
            return Sijoitus(uusi_kohde, korvaa(arvo, nimi, uusi), rivi)
        case Kirjoita(virta, arvo, rivi):
            return Kirjoita(virta, korvaa(arvo, nimi, uusi), rivi)
        case Jos(ehto, tosi, epatosi, rivi):
            return Jos(korvaa(ehto, nimi, uusi),
                       [korvaa_lause(x, nimi, uusi) for x in tosi],
                       [korvaa_lause(x, nimi, uusi) for x in epatosi], rivi)
        case Silmukka():
            return replace(lause, runko=[korvaa_lause(x, nimi, uusi)
                                         for x in lause.runko])
        case Palauta(arvo, rivi):
            return Palauta(korvaa(arvo, nimi, uusi), rivi)


# @alku avaa
def avaa(lauseet: list[Lause], kaikki: bool = False) -> list[Lause]:
    """Avaa silmukat, joissa on unroll-pragma. Jos kaikki on tosi,
    avataan kaikki silmukat kokonaan (liukuhihnoitetun silmukan
    sisäsilmukat)."""
    tulos: list[Lause] = []
    for lause in lauseet:
        if isinstance(lause, Jos):
            tulos.append(Jos(lause.ehto, avaa(lause.tosi, kaikki),
                             avaa(lause.epatosi, kaikki), lause.rivi))
            continue
        if not isinstance(lause, Silmukka):
            tulos.append(lause)
            continue
        pragmat = {p.laji: p for p in lause.pragmat}
        liukuhihna = "pipeline" in pragmat
        runko = avaa(lause.runko, kaikki or liukuhihna)
        if kaikki or ("unroll" in pragmat and
                      "factor" not in pragmat["unroll"].asetukset):
            for k in range(lause.kierrokset):           # kokonaan
                arvo = Luku(lause.alku + k * lause.askel)
                tulos.extend(korvaa_lause(x, lause.muuttuja, arvo)
                             for x in runko)
            continue
        tekija = 1
        if "unroll" in pragmat:
            tekija = int(pragmat["unroll"].asetukset["factor"])
            if lause.kierrokset % tekija:
                raise KaannosVirhe(lause.rivi, "kierrosmäärä ei ole "
                                   f"jaollinen avauskertoimella {tekija}")
        uusi_runko: list[Lause] = []
        for k in range(tekija):                         # osittain
            siirto = Binaari("+", Nimi(lause.muuttuja),
                             Luku(k * lause.askel))
            uusi = Nimi(lause.muuttuja) if k == 0 else siirto
            uusi_runko.extend(korvaa_lause(x, lause.muuttuja, uusi)
                              for x in runko)
        tulos.append(replace(lause, askel=lause.askel * tekija,
                             kierrokset=lause.kierrokset // tekija,
                             runko=uusi_runko))
    return tulos
# @loppu avaa


# @alku alueet
@dataclass
class Lehti:
    """Suoraviivainen koodi, joka suoritetaan kierrokset kertaa.
    Silmukan runko on lehti, jolla on silmukkamuuttuja; silmukoiden
    väliin jäävä koodi on lehti, jolla kierroksia on yksi."""
    nimi: str
    lauseet: list[Lause]
    muuttuja: str | None = None
    alku: int = 0
    askel: int = 1
    kierrokset: int = 1
    ii: int | None = None           # pyydetty aloitusväli, jos pipeline


@dataclass
class Ulompi:
    """Silmukka, jonka rungossa on silmukoita."""
    nimi: str
    muuttuja: str
    alku: int
    askel: int
    kierrokset: int
    runko: list[Lehti | Ulompi] = field(default_factory=list)


def alueet(lauseet: list[Lause]) -> list[Lehti | Ulompi]:
    tulos: list[Lehti | Ulompi] = []
    suora: list[Lause] = []

    def sulje() -> None:
        if suora:
            tulos.append(Lehti(f"lohko{len(tulos) + 1}", list(suora)))
            suora.clear()

    for lause in lauseet:
        if not isinstance(lause, Silmukka):
            if isinstance(lause, Jos) and sisaltaa_silmukan(lause):
                raise KaannosVirhe(lause.rivi, "silmukka ehtolauseen sisällä "
                                   "ei ole tuettu")
            suora.append(lause)
            continue
        sulje()
        pragmat = {p.laji: p for p in lause.pragmat}
        if any(sisaltaa_silmukan(x) for x in lause.runko):
            if "pipeline" in pragmat:
                raise KaannosVirhe(lause.rivi, "sisäsilmukat olisi pitänyt "
                                   "avata")
            tulos.append(Ulompi(lause.nimi, lause.muuttuja, lause.alku,
                                lause.askel, lause.kierrokset,
                                alueet(lause.runko)))
            continue
        ii = None
        if "pipeline" in pragmat:
            ii = int(pragmat["pipeline"].asetukset.get("II", "1"))
        tulos.append(Lehti(lause.nimi, lause.runko, lause.muuttuja,
                           lause.alku, lause.askel, lause.kierrokset, ii))
    sulje()
    return tulos
# @loppu alueet


def sisaltaa_silmukan(lause: Lause) -> bool:
    if isinstance(lause, Silmukka):
        return True
    if isinstance(lause, Jos):
        return any(sisaltaa_silmukan(x) for x in lause.tosi + lause.epatosi)
    return False


def lue_kaikki(lauseke: Lauseke) -> set[str]:
    """Lausekkeen lukemat muuttujat (taulukoiden alkiot muodossa a[3])."""
    match lauseke:
        case Nimi(n):
            return {n}
        case Indeksi(taulu, Luku(k)):
            return {f"{taulu}[{k}]", taulu}
        case Indeksi(taulu, indeksi):
            return {taulu} | lue_kaikki(indeksi)
        case Binaari(_, vasen, oikea):
            return lue_kaikki(vasen) | lue_kaikki(oikea)
        case Unaari(_, arvo):
            return lue_kaikki(arvo)
        case Ehto(e, t, f):
            return lue_kaikki(e) | lue_kaikki(t) | lue_kaikki(f)
        case Lue() | Luku():
            return set()


def luetut(lauseet: list[Lause]) -> set[str]:
    tulos: set[str] = set()
    for lause in lauseet:
        match lause:
            case Sijoitus(kohde, arvo, _):
                tulos |= lue_kaikki(arvo)
                if isinstance(kohde, Indeksi):
                    tulos |= lue_kaikki(kohde.indeksi)
            case Kirjoita(_, arvo, _) | Palauta(arvo, _):
                tulos |= lue_kaikki(arvo)
            case Jos(ehto, tosi, epatosi, _):
                tulos |= lue_kaikki(ehto) | luetut(tosi) | luetut(epatosi)
            case Silmukka():
                tulos |= luetut(lause.runko)
    return tulos
