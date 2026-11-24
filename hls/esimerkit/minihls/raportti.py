"""Synteesiraportti: alueiden ajoitus, latenssi ja resurssit."""

from __future__ import annotations

from .ajoitus import alap, asap, yksikkopituus
from .dfg import Dfg, Operandi, Solmu, Vakaa, Vakio
from .sidonta import Lehtiajoitus


def teksti(o: Operandi) -> str:
    if isinstance(o, Vakio):
        return str(o.arvo)
    if isinstance(o, Vakaa):
        return o.nimi.removeprefix("m_")
    return f"t{o.solmu}"


def kuvaus(s: Solmu) -> str:
    """Solmu luettavassa muodossa, esim. t7 = t5 * t6."""
    a = [teksti(o) for o in s.syotteet]
    taulu = s.kohde
    tulos = f"t{s.id} = "
    match s.laji:
        case "iteraatio":
            return tulos + "i (kierros)"
        case "muuttuja":
            return tulos + s.kohde
        case "lataa":
            return tulos + f"{taulu}[{a[0]}]" + pankki(s)
        case "tallenna":
            ehto = "" if s.ehto is None else f" jos {teksti(s.ehto)}"
            return f"{taulu}[{a[0]}] = {a[1]}{pankki(s)}{ehto}"
        case "kirjoita":
            return f"{s.kohde} = {a[0]}"
        case "palauta":
            return f"return {a[0]}"
        case "lue_virta":
            return tulos + f"{s.kohde}.read()"
        case "kirjoita_virta":
            return f"{s.kohde}.write({a[0]})"
        case "valinta":
            return tulos + f"{a[0]} ? {a[1]} : {a[2]}"
        case "laajenna":
            return tulos + f"laajenna({a[0]})"
        case "~":
            return tulos + f"~{a[0]}"
    return tulos + f" {s.laji} ".join(a)


def pankki(s: Solmu) -> str:
    return f" (pankki {s.pankki})" if s.pankkeja > 1 else ""


def dfg(g: Dfg) -> list[str]:
    rivit = [kuvaus(s) for _, s in sorted(g.solmut.items())]
    rivit += [f"järjestys: t{r.lahto} -> t{r.kohde} (viive {r.viive})"
              for r in g.reunat]
    rivit += [f"kantava: t{k.lahto} -> t{k.kohde} (viive {k.viive}, "
              f"etäisyys {k.etaisyys}): {k.syy}" for k in g.kantavat]
    return rivit


# @alku asap
def asap_alap(g: Dfg) -> list[str]:
    a = asap(g)
    pituus = yksikkopituus(g, a)
    b = alap(g, pituus)
    rivit = [f"{'operaatio':<26}{'ASAP':>5}{'ALAP':>5}{'liikkuvuus':>11}"]
    for i, s in sorted(g.solmut.items()):
        rivit.append(f"{kuvaus(s):<26}{a[i]:>5}{b[i]:>5}{b[i] - a[i]:>11}")
    rivit.append(f"pituus {pituus} jaksoa (yksikköviiveet)")
    return rivit
# @loppu asap


def ajoitus(lehti: Lehtiajoitus, kertojat: dict[int, int]) -> list[str]:
    rivit = [f"{lehti.nimi}: pituus {lehti.t.pituus}, II {lehti.ii}, "
             f"vaiheita {lehti.vaiheet}"]
    for jakso in range(lehti.t.pituus):
        solmut = [s for _, s in sorted(lehti.g.solmut.items())
                  if lehti.t.jakso[s.id] == jakso]
        for n, s in enumerate(solmut):
            alku = f"  {jakso:>3}" if n == 0 else "     "
            lisa = f"  [mul{kertojat[s.id]}]" if s.id in kertojat else ""
            valmis = lehti.t.saapuu[s.id]
            aika = f"{valmis:4.1f} ns" if s.laji not in (
                "tallenna", "kirjoita", "palauta", "kirjoita_virta") else ""
            rivit.append(f"{alku}  {kuvaus(s) + lisa:<44}{aika:>8}".rstrip())
    return rivit


# @alku yhteenveto
def yhteenveto(nimi: str, kello: float, lehdet: list[Lehtiajoitus],
               toistot: dict[int, int], kertojia: int) -> list[str]:
    rivit = [f"minihls: {nimi}, kellojakso {kello:g} ns",
             f"{'alue':<14}{'kierr.':>7}{'pituus':>7}{'II':>4}"
             f"{'vaiheet':>8}{'latenssi':>9}{'toistot':>8}"]
    yhteensa = 0
    for x in lehdet:
        rivit.append(f"{x.nimi:<14}{x.kierrokset:>7}{x.t.pituus:>7}"
                     f"{x.ii:>4}{x.vaiheet:>8}{x.latenssi:>9}"
                     f"{toistot[x.numero]:>8}")
        yhteensa += x.latenssi * toistot[x.numero]
    rivit.append(f"latenssi {yhteensa + 1} jaksoa (alueet {yhteensa}, "
                 "käynnistys 1)")
    for x in lehdet:
        if x.pyydetty_ii is not None and x.ii > x.pyydetty_ii:
            rivit.append(f"{x.nimi}: II {x.ii}, pyydettiin {x.pyydetty_ii}, "
                         "koska")
            rivit += [f"  {syy}" for syy in x.syyt]
    lajit: dict[str, int] = {}
    for x in lehdet:
        for s in x.g.solmut.values():
            lajit[s.laji] = lajit.get(s.laji, 0) + 1
    summaimia = lajit.get("+", 0) + lajit.get("-", 0)
    vertailuja = sum(lajit.get(v, 0) for v in ("<", "<=", ">", ">=",
                                                "==", "!="))
    rivit.append(f"kertojia {kertojia}, summaimia {summaimia}, "
                 f"vertailuja {vertailuja}, valintoja "
                 f"{lajit.get('valinta', 0)}")
    return rivit
# @loppu yhteenveto
