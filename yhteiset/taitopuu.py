#!/usr/bin/env python3
"""Taitopuun tarkistin ja generaattori.

Käyttö:
  taitopuu.py tarkista <taitopuu.toml> [--readme README.md]
  taitopuu.py generoi  <taitopuu.toml> <kohdehakemisto> [--readme README.md]

`tarkista` varmistaa, että taitopuu on eheä:
  - tunnisteet ovat yksikäsitteisiä ja viittaukset osuvat olemassa
    oleviin alueisiin, taitoihin ja roadmap.sh-polkuihin,
  - esitietoverkossa ei ole syklejä eikä tarpeettomia kaaria (jos A
    edellyttää B:tä ja B C:tä, A ei saa luetella C:tä erikseen),
  - jokainen taito kuuluu vähintään yhteen roolipolkuun,
  - valmiiksi merkityn tutoriaalin hakemisto on olemassa,
  - README on ajan tasalla (jos --readme annetaan).

`generoi` kirjoittaa kohdehakemistoon PDF:n generoidut luvut (Markdown)
ja kaaviot (Graphviz, PDF), sekä halutessa README-tiedoston, jossa on
GitHubissa piirtyvä Mermaid-kaavio.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

TUNNISTE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Alueiden värit kaavioissa (vaaleat taustat, jotta teksti erottuu).
VARIT = ["#DCE8F5", "#F5E6D3", "#E3F0DA", "#EEE0F2", "#FCE4E4",
         "#DDF1EF", "#F7F0CF", "#E6E6E6", "#E2E7F8", "#F2DDE8",
         "#E8F2D0", "#FBE3D3"]
VALMIS_REUNA = "#2E7D32"


@dataclass
class Taito:
    id: str
    nimi: str
    alue: str
    kuvaus: str
    edellyttaa: list[str]
    aiheet: list[str]
    laajuus: int
    testaus: str
    roadmap: list[str]
    amk: str
    tutoriaali: str | None = None
    nippu: str | None = None
    taso: int = 0
    seuraajat: list[str] = field(default_factory=list)

    @property
    def valmis(self) -> bool:
        return self.tutoriaali is not None


@dataclass
class Rooli:
    id: str
    nimi: str
    kuvaus: str
    tavoitteet: list[str]
    valinnaiset: list[str]


@dataclass
class Puu:
    alueet: dict[str, dict]
    taidot: dict[str, Taito]
    roolit: dict[str, Rooli]
    lahteet: dict
    juuri: Path   # repositorion juuri

    def esitiedot(self, tid: str) -> set[str]:
        """Taidon kaikki (transitiiviset) esitiedot."""
        tulos: set[str] = set()
        pino = list(self.taidot[tid].edellyttaa)
        while pino:
            t = pino.pop()
            if t not in tulos:
                tulos.add(t)
                pino.extend(self.taidot[t].edellyttaa)
        return tulos

    def jalkelaiset(self, tid: str) -> set[str]:
        tulos: set[str] = set()
        pino = list(self.taidot[tid].seuraajat)
        while pino:
            t = pino.pop()
            if t not in tulos:
                tulos.add(t)
                pino.extend(self.taidot[t].seuraajat)
        return tulos

    def polku(self, rid: str) -> set[str]:
        """Roolin pakolliset taidot: tavoitteet ja niiden esitiedot."""
        tulos: set[str] = set()
        for t in self.roolit[rid].tavoitteet:
            tulos.add(t)
            tulos |= self.esitiedot(t)
        return tulos

    def jarjesta(self, joukko) -> list[Taito]:
        alueet = list(self.alueet)
        return sorted((self.taidot[t] for t in joukko),
                      key=lambda t: (t.taso, alueet.index(t.alue), t.nimi))

    def roolit_taidolle(self, tid: str) -> list[Rooli]:
        return [r for r in self.roolit.values() if tid in self.polku(r.id)]


class Virhe(Exception):
    pass


def lataa(polku: Path) -> tuple[Puu, list[str]]:
    data = tomllib.loads(polku.read_text("utf-8"))
    virheet: list[str] = []

    def vaadi(kohde: dict, avaimet: list[str], paikka: str):
        for a in avaimet:
            if a not in kohde:
                virheet.append(f"{paikka}: kenttä '{a}' puuttuu")

    alueet = {}
    for a in data.get("alue", []):
        vaadi(a, ["id", "nimi", "kuvaus"], f"alue {a.get('id')}")
        if a.get("id") in alueet:
            virheet.append(f"alue {a['id']}: tunniste toistuu")
        alueet[a.get("id")] = a

    taidot: dict[str, Taito] = {}
    kentat = ["id", "nimi", "alue", "kuvaus", "edellyttaa", "aiheet",
              "laajuus", "testaus", "roadmap", "amk"]
    for t in data.get("taito", []):
        vaadi(t, kentat, f"taito {t.get('id')}")
        tuntemattomat = set(t) - set(kentat) - {"tutoriaali", "nippu"}
        if tuntemattomat:
            virheet.append(f"taito {t.get('id')}: tuntemattomat kentät "
                           f"{sorted(tuntemattomat)}")
        if virheet:
            continue
        if t["id"] in taidot:
            virheet.append(f"taito {t['id']}: tunniste toistuu")
        taidot[t["id"]] = Taito(**{k: t[k] for k in kentat},
                                tutoriaali=t.get("tutoriaali"),
                                nippu=t.get("nippu"))

    roolit: dict[str, Rooli] = {}
    for r in data.get("rooli", []):
        vaadi(r, ["id", "nimi", "kuvaus", "tavoitteet", "valinnaiset"],
              f"rooli {r.get('id')}")
        if virheet:
            continue
        if r["id"] in roolit:
            virheet.append(f"rooli {r['id']}: tunniste toistuu")
        roolit[r["id"]] = Rooli(**r)

    puu = Puu(alueet, taidot, roolit, data.get("lahteet", {}),
              polku.resolve().parent.parent)
    if not virheet:
        virheet += tarkista_rakenne(puu)
    return puu, virheet


def tarkista_rakenne(puu: Puu) -> list[str]:
    v: list[str] = []
    tunnetut_polut = set(puu.lahteet.get("roadmap_polut", []))

    for kokoelma in (puu.alueet, puu.taidot, puu.roolit):
        for tid in kokoelma:
            if not TUNNISTE.match(tid):
                v.append(f"{tid}: tunnisteen on oltava muotoa a-z0-9-")

    for t in puu.taidot.values():
        if t.alue not in puu.alueet:
            v.append(f"{t.id}: tuntematon alue '{t.alue}'")
        if not isinstance(t.laajuus, int) or not 1 <= t.laajuus <= 15:
            v.append(f"{t.id}: laajuuden on oltava 1–15 op")
        if len(t.aiheet) < 3:
            v.append(f"{t.id}: aiheita on oltava vähintään kolme")
        for e in t.edellyttaa:
            if e not in puu.taidot:
                v.append(f"{t.id}: tuntematon esitieto '{e}'")
            elif e == t.id:
                v.append(f"{t.id}: edellyttää itseään")
        if len(set(t.edellyttaa)) != len(t.edellyttaa):
            v.append(f"{t.id}: esitieto toistuu")
        for r in t.roadmap:
            if r not in tunnetut_polut:
                v.append(f"{t.id}: roadmap.sh-polkua '{r}' ei ole "
                         "lahteet.roadmap_polut-luettelossa")
        if t.tutoriaali is not None:
            hak = puu.juuri / t.tutoriaali
            if not (hak / "Makefile").exists():
                v.append(f"{t.id}: tutoriaalin hakemistoa {hak} ei ole "
                         "tai siitä puuttuu Makefile")
    if v:
        return v

    # Syklit: syvyyshaku kolmella värillä.
    tila: dict[str, int] = {}

    def kay(tid: str, pino: list[str]):
        tila[tid] = 1
        for e in puu.taidot[tid].edellyttaa:
            if tila.get(e) == 1:
                sykli = pino[pino.index(e):] + [e] if e in pino else [e]
                v.append("sykli: " + " -> ".join(sykli))
            elif e not in tila:
                kay(e, pino + [e])
        tila[tid] = 2

    for tid in puu.taidot:
        if tid not in tila:
            kay(tid, [tid])
    if v:
        return v

    # Seuraajat ja tasot.
    for t in puu.taidot.values():
        for e in t.edellyttaa:
            puu.taidot[e].seuraajat.append(t.id)

    def taso(tid: str) -> int:
        t = puu.taidot[tid]
        if t.taso == 0:
            t.taso = 1 + max((taso(e) for e in t.edellyttaa), default=0)
        return t.taso

    for tid in puu.taidot:
        taso(tid)

    # Tarpeettomat kaaret: esitieto, joka sisältyy toisen esitiedon
    # esitietoihin.
    for t in puu.taidot.values():
        for e in t.edellyttaa:
            for muu in t.edellyttaa:
                if muu != e and e in puu.esitiedot(muu):
                    v.append(f"{t.id}: esitieto '{e}' on tarpeeton, koska "
                             f"'{muu}' edellyttää sitä jo")

    # Roolit.
    kaytetyt: set[str] = set()
    for r in puu.roolit.values():
        tuntemattomat = [t for t in r.tavoitteet + r.valinnaiset
                         if t not in puu.taidot]
        for t in tuntemattomat:
            v.append(f"rooli {r.id}: tuntematon taito '{t}'")
        if tuntemattomat:
            continue
        polku = puu.polku(r.id)
        for t in r.tavoitteet:
            if any(t in puu.esitiedot(muu) for muu in r.tavoitteet):
                v.append(f"rooli {r.id}: tavoite '{t}' sisältyy jo "
                         "toiseen tavoitteeseen")
        for t in r.valinnaiset:
            if t in polku:
                v.append(f"rooli {r.id}: valinnainen '{t}' kuuluu jo "
                         "pakolliseen polkuun")
        kaytetyt |= polku | set(r.valinnaiset)
    for tid in puu.taidot:
        if tid not in kaytetyt:
            v.append(f"{tid}: taito ei kuulu yhteenkään rooliin")
    return v


# ---------------------------------------------------------------------
# Kaaviot
# ---------------------------------------------------------------------

def alueen_vari(puu: Puu, alue: str) -> str:
    return VARIT[list(puu.alueet).index(alue) % len(VARIT)]


def solmu(puu: Puu, t: Taito, korosta: bool = True) -> str:
    nimi = t.nimi.replace('"', '\\"')
    merkki = "✓ " if t.valmis else ""
    tyyli = 'style="filled,rounded"'
    reuna = (f', color="{VALMIS_REUNA}", penwidth=2.2'
             if t.valmis else ', color="#555555"')
    vari = alueen_vari(puu, t.alue) if korosta else "#F4F4F4"
    return (f'  "{t.id}" [label="{merkki}{nimi}\\n{t.laajuus} op", '
            f'{tyyli}, fillcolor="{vari}"{reuna}];')


def dot_alku(nimi: str, suunta: str = "LR") -> list[str]:
    return [f"digraph {nimi} {{",
            f'  rankdir={suunta}; ranksep=0.45; nodesep=0.18;',
            '  node [shape=box, fontname="Latin Modern Sans", '
            'fontsize=10, margin="0.08,0.04"];',
            '  edge [color="#777777", arrowsize=0.6];']


def kokonaiskuva_dot(puu: Puu) -> str:
    r = dot_alku("kokonaiskuva", "LR")
    for aid, alue in puu.alueet.items():
        r.append(f'  subgraph "cluster_{aid}" {{')
        r.append(f'    label="{alue["nimi"]}"; fontname="Latin Modern '
                 f'Sans"; fontsize=11; style="rounded"; '
                 f'color="#BBBBBB";')
        for t in puu.taidot.values():
            if t.alue == aid:
                r.append("  " + solmu(puu, t))
        r.append("  }")
    for t in puu.taidot.values():
        for e in t.edellyttaa:
            r.append(f'  "{e}" -> "{t.id}";')
    r.append("}")
    return "\n".join(r)


def alueet_dot(puu: Puu) -> str:
    r = dot_alku("alueet", "LR")
    kaaret: dict[tuple[str, str], int] = defaultdict(int)
    for t in puu.taidot.values():
        for e in t.edellyttaa:
            a = puu.taidot[e].alue
            if a != t.alue:
                kaaret[(a, t.alue)] += 1
    for aid, alue in puu.alueet.items():
        op = sum(t.laajuus for t in puu.taidot.values() if t.alue == aid)
        n = sum(1 for t in puu.taidot.values() if t.alue == aid)
        r.append(f'  "{aid}" [label="{alue["nimi"]}\\n{n} taitoa, {op} op",'
                 f' style="filled,rounded", fillcolor="{alueen_vari(puu, aid)}"'
                 f', fontsize=11];')
    for (a, b), n in sorted(kaaret.items()):
        r.append(f'  "{a}" -> "{b}" [penwidth={0.6 + 0.4 * n:.1f}];')
    r.append("}")
    return "\n".join(r)


def rooli_dot(puu: Puu, rid: str) -> str:
    rooli = puu.roolit[rid]
    polku = puu.polku(rid)
    mukana = polku | set(rooli.valinnaiset)
    r = dot_alku(f'"{rid}"', "LR")
    for tid in mukana:
        t = puu.taidot[tid]
        rivi = solmu(puu, t)
        if tid in rooli.valinnaiset:
            rivi = rivi.replace('style="filled,rounded"',
                                'style="filled,rounded,dashed"')
        r.append(rivi)
    for tid in mukana:
        for e in puu.taidot[tid].edellyttaa:
            if e in mukana:
                r.append(f'  "{e}" -> "{tid}";')
    # Valinnaisten esitiedot, jotka eivät ole polulla, näytetään harmaina.
    for tid in rooli.valinnaiset:
        for e in puu.taidot[tid].edellyttaa:
            if e not in mukana:
                r.append(solmu(puu, puu.taidot[e], korosta=False))
                r.append(f'  "{e}" -> "{tid}" [style=dashed];')
    r.append("}")
    return "\n".join(r)


def piirra(dot: str, kohde: Path):
    kohde.parent.mkdir(parents=True, exist_ok=True)
    kohde.with_suffix(".dot").write_text(dot, "utf-8")
    subprocess.run(["dot", "-Tpdf", "-o", str(kohde)],
                   input=dot.encode("utf-8"), check=True)


# ---------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------

def kuva(polku: str, korkeus: str = "0.5", kaanna: bool = False) -> str:
    """LaTeX-lohko kuvalle; säilyttää kuvasuhteen ja rajaa korkeuden.
    Leveä kuva voidaan kääntää 90 astetta, jolloin se täyttää sivun."""
    kulma = "angle=90," if kaanna else ""
    komento = (f"\\begin{{center}}\n\\includegraphics[{kulma}"
               f"width=\\linewidth,height={korkeus}\\textheight,"
               f"keepaspectratio]{{{polku}}}\n\\end{{center}}")
    if kaanna:
        komento = f"\\clearpage\n{komento}\n\\clearpage"
    return f"```{{=latex}}\n{komento}\n```"


def nimet(puu: Puu, tunnisteet) -> str:
    if not tunnisteet:
        return "–"
    return ", ".join(puu.taidot[t].nimi for t in
                     sorted(tunnisteet, key=lambda x: puu.taidot[x].nimi))


def tila_teksti(t: Taito) -> str:
    return f"valmis (`{t.tutoriaali}`)" if t.valmis else "suunniteltu"


def luku_kokonaiskuva(puu: Puu, kuvat: str) -> str:
    valmiit = [t for t in puu.taidot.values() if t.valmis]
    op = sum(t.laajuus for t in puu.taidot.values())
    r = ["# Kokonaiskuva", "",
         f"Taitopuussa on {len(puu.taidot)} taitoa {len(puu.alueet)} "
         f"alueella, yhteensä noin {op} opintopistettä. Valmiita "
         f"tutoriaaleja on {len(valmiit)}.", "",
         "## Alueet", "",
         "Alla oleva kaavio näyttää, miten alueet nojaavat toisiinsa. "
         "Nuoli alueelta A alueelle B tarkoittaa, että jokin B:n taito "
         "edellyttää A:n taitoa; nuolen paksuus kertoo, kuinka monta "
         "tällaista riippuvuutta on.", "",
         kuva(f"{kuvat}/alueet.pdf", "0.35"), "",
         "| Alue | Taitoja | op | Kuvaus |",
         "|" + "-" * 22 + "|" + "-" * 7 + ":|" + "-" * 4 + ":|"
         + "-" * 55 + "|"]
    for aid, a in puu.alueet.items():
        ts = [t for t in puu.taidot.values() if t.alue == aid]
        r.append(f"| {a['nimi']} | {len(ts)} | "
                 f"{sum(t.laajuus for t in ts)} | {a['kuvaus']} |")
    r += ["", "## Koko taitopuu", "",
          "Seuraavalla sivulla on koko taitopuu käännettynä vaakasuuntaan. Kukin laatikko on yksi "
          "tutoriaali, ja nuoli osoittaa esitiedosta siihen taitoon, jonka "
          "se mahdollistaa. Valmiit tutoriaalit on merkitty vihreällä "
          "reunalla ja valintamerkillä.", "",
          kuva(f"{kuvat}/kokonaiskuva.pdf", "0.95", kaanna=True), ""]
    return "\n".join(r)


def luku_roolit(puu: Puu, kuvat: str) -> str:
    r = ["# Roolipolut", "",
         "Rooli on ammattiprofiili, joka määritellään tavoitetaitoina. "
         "Roolin polku koostuu tavoitteista ja kaikista niiden "
         "esitiedoista. Taidot on lueteltu järjestyksessä, jossa ne voi "
         "opiskella: jokaisen taidon esitiedot ovat listassa ennen sitä. "
         "Saman tason taidot ovat toisistaan riippumattomia, ja ne voi "
         "opiskella missä järjestyksessä tahansa tai rinnakkain.", "",
         "Kaavioissa katkoviivalla reunustetut taidot ovat valinnaisia "
         "syventäviä taitoja. Harmaat taidot ovat valinnaisten taitojen "
         "esitietoja, jotka eivät kuulu roolin pakolliseen polkuun.", "",
         "| Rooli | Taitoja | op | Valmiina |",
         "|-------|--------:|---:|---------:|"]
    for rid, rooli in puu.roolit.items():
        p = puu.polku(rid)
        op = sum(puu.taidot[t].laajuus for t in p)
        valmiina = sum(1 for t in p if puu.taidot[t].valmis)
        r.append(f"| {rooli.nimi} | {len(p)} | {op} | {valmiina} |")
    r.append("")
    for rid, rooli in puu.roolit.items():
        p = puu.polku(rid)
        op = sum(puu.taidot[t].laajuus for t in p)
        r += [f"## {rooli.nimi}", "", rooli.kuvaus, "",
              f"**Tavoitteet:** {nimet(puu, rooli.tavoitteet)}. "
              f"**Laajuus:** {len(p)} taitoa, noin {op} op.", "",
              kuva(f"{kuvat}/rooli-{rid}.pdf", "0.45"), "",
              "| Taso | Taito | Alue | op | Tila |",
              "|" + "-" * 4 + ":|" + "-" * 38 + "|" + "-" * 24 + "|"
              + "-" * 3 + ":|" + "-" * 20 + "|"]
        for t in puu.jarjesta(p):
            r.append(f"| {t.taso} | {t.nimi} | "
                     f"{puu.alueet[t.alue]['nimi']} | {t.laajuus} | "
                     f"{tila_teksti(t)} |")
        if rooli.valinnaiset:
            r += ["", "Valinnaiset syventävät taidot: "
                  f"{nimet(puu, rooli.valinnaiset)}."]
        r.append("")
    return "\n".join(r)


def luku_taidot(puu: Puu) -> str:
    r = ["# Taidot", "",
         "Tässä luvussa on jokaisen taidon kuvaus ja suunniteltu sisältö "
         "alueittain. *Taso* on pisimmän esitietoketjun pituus: tason 1 "
         "taidoilla ei ole esitietoja. *Mahdollistaa* luettelee taidot, "
         "joiden välitön esitieto taito on.", ""]
    for aid, alue in puu.alueet.items():
        r += [f"## {alue['nimi']}", "", alue["kuvaus"], ""]
        for t in puu.jarjesta(tid for tid, x in puu.taidot.items()
                              if x.alue == aid):
            roolit = ", ".join(x.nimi for x in puu.roolit_taidolle(t.id))
            lahteet = ", ".join(f"`{s}`" for s in t.roadmap) or "–"
            r += [f"### {t.nimi}", "", t.kuvaus, "",
                  f"- **Laajuus ja taso:** {t.laajuus} op, taso {t.taso}",
                  f"- **Edellyttää:** {nimet(puu, t.edellyttaa)}",
                  f"- **Mahdollistaa:** {nimet(puu, t.seuraajat)}",
                  f"- **Roolit:** {roolit or '– (vain valinnainen)'}",
                  f"- **Tila:** {tila_teksti(t)}",
                  f"- **Testaus:** {t.testaus}",
                  f"- **Vastaavuudet:** roadmap.sh {lahteet}; "
                  f"AMK: {t.amk}",
                  "", "Aiheet:", ""]
            r += [f"1. {a}" for a in t.aiheet]
            r.append("")
    return "\n".join(r)


def tuotantojarjestys(puu: Puu) -> list[tuple[Taito, int, int, int]]:
    rivit = []
    for t in puu.taidot.values():
        if t.valmis:
            continue
        roolit = len(puu.roolit_taidolle(t.id))
        jalk = len(puu.jalkelaiset(t.id))
        valmiit = sum(1 for e in t.edellyttaa if puu.taidot[e].valmis)
        rivit.append((t, roolit, jalk, valmiit))
    rivit.sort(key=lambda x: (-x[1], -x[2], x[0].taso, x[0].nimi))
    return rivit


def luku_tuotanto(puu: Puu) -> str:
    r = ["# Tutoriaalien tuotantojärjestys", "",
         "Taulukko järjestää kirjoittamattomat tutoriaalit sen mukaan, "
         "kuinka moneen roolipolkuun ne kuuluvat ja kuinka monen muun "
         "taidon esitietoihin ne sisältyvät. Ylimmät tutoriaalit hyödyttävät "
         "eniten oppijoita ja avaavat eniten jatkoa. Sarake *Esitiedot "
         "valmiina* kertoo, kuinka monelle välittömälle esitiedolle on jo "
         "tutoriaali.", "",
         "| # | Taito | Taso | Rooleja | Mahdollistaa | Esitiedot valmiina |",
         "|" + "-" * 3 + ":|" + "-" * 42 + "|" + "-" * 5 + ":|"
         + "-" * 7 + ":|" + "-" * 11 + ":|" + "-" * 9 + ":|"]
    for i, (t, roolit, jalk, valmiit) in enumerate(tuotantojarjestys(puu),
                                                    1):
        r.append(f"| {i} | {t.nimi} | {t.taso} | {roolit} | {jalk} | "
                 f"{valmiit}/{len(t.edellyttaa)} |")
    r.append("")
    return "\n".join(r)


def readme(puu: Puu) -> str:
    op = sum(t.laajuus for t in puu.taidot.values())
    r = ["<!-- Tämä tiedosto on generoitu tiedostosta taitopuu.toml",
         "     komennolla `make readme`. Älä muokkaa käsin. -->", "",
         "# Opintopolut", "",
         "Tutoriaalit muodostavat taitopuun: jokainen tutoriaali on yksi "
         "taito, ja taidot rakentuvat toistensa päälle. Roolit ovat "
         "ammattiprofiileja, joiden polku kulkee puun läpi.", "",
         f"Taitoja on {len(puu.taidot)}, yhteensä noin {op} op. "
         "Valmis PDF: [opintopolut.pdf](opintopolut.pdf). "
         "Taitopuun lähdetiedosto: [taitopuu.toml](taitopuu.toml).", "",
         "## Roolit", "",
         "| Rooli | Tavoitteet | Taitoja | op |",
         "|-------|------------|--------:|---:|"]
    for rid, rooli in puu.roolit.items():
        p = puu.polku(rid)
        r.append(f"| {rooli.nimi} | {nimet(puu, rooli.tavoitteet)} | "
                 f"{len(p)} | {sum(puu.taidot[t].laajuus for t in p)} |")
    r += ["", "## Taitopuu", "",
          "Valmiit tutoriaalit on merkitty merkillä ✓.", "",
          "```mermaid", "flowchart LR"]
    for aid, alue in puu.alueet.items():
        r.append(f'  subgraph {aid}["{alue["nimi"]}"]')
        for t in puu.taidot.values():
            if t.alue == aid:
                merkki = "✓ " if t.valmis else ""
                r.append(f'    {t.id.replace("-", "_")}'
                         f'["{merkki}{t.nimi}"]')
        r.append("  end")
    for t in puu.taidot.values():
        for e in t.edellyttaa:
            r.append(f'  {e.replace("-", "_")} --> '
                     f'{t.id.replace("-", "_")}')
    r += ["```", "", "## Taidot alueittain", ""]
    for aid, alue in puu.alueet.items():
        r += [f"### {alue['nimi']}", "",
              "| Taito | op | Edellyttää | Tila |",
              "|-------|---:|------------|------|"]
        for t in puu.jarjesta(tid for tid, x in puu.taidot.items()
                              if x.alue == aid):
            tila = (f"[valmis](../{t.tutoriaali}/)" if t.valmis
                    else "suunniteltu")
            r.append(f"| {t.nimi} | {t.laajuus} | "
                     f"{nimet(puu, t.edellyttaa)} | {tila} |")
        r.append("")
    return "\n".join(r)


def generoi(puu: Puu, kohde: Path):
    kuvat = kohde / "kuvat"
    piirra(alueet_dot(puu), kuvat / "alueet.pdf")
    piirra(kokonaiskuva_dot(puu), kuvat / "kokonaiskuva.pdf")
    for rid in puu.roolit:
        piirra(rooli_dot(puu, rid), kuvat / f"rooli-{rid}.pdf")
    luvut = kohde / "luvut"
    luvut.mkdir(parents=True, exist_ok=True)
    polku = kuvat.as_posix()
    (luvut / "02-kokonaiskuva.md").write_text(
        luku_kokonaiskuva(puu, polku), "utf-8")
    (luvut / "03-roolit.md").write_text(luku_roolit(puu, polku), "utf-8")
    (luvut / "04-taidot.md").write_text(luku_taidot(puu), "utf-8")
    (luvut / "05-tuotanto.md").write_text(luku_tuotanto(puu), "utf-8")


def main() -> int:
    jasennin = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    jasennin.add_argument("komento", choices=["tarkista", "generoi"])
    jasennin.add_argument("toml", type=Path)
    jasennin.add_argument("kohde", type=Path, nargs="?")
    jasennin.add_argument("--readme", type=Path)
    jasennin.add_argument("--kirjoita-readme", action="store_true",
                          help="kirjoita README tarkistamisen sijaan")
    a = jasennin.parse_args()

    puu, virheet = lataa(a.toml)
    if virheet:
        print("\n".join(virheet))
        print(f"\nVIRHEITÄ: {len(virheet)}")
        return 1

    if a.readme:
        sisalto = readme(puu)
        if a.kirjoita_readme:
            a.readme.write_text(sisalto, "utf-8")
        elif not a.readme.exists() or \
                a.readme.read_text("utf-8") != sisalto:
            print(f"{a.readme} ei ole ajan tasalla: aja `make readme`")
            return 1

    if a.komento == "generoi":
        if a.kohde is None:
            jasennin.error("generoi tarvitsee kohdehakemiston")
        generoi(puu, a.kohde)
    op = sum(t.laajuus for t in puu.taidot.values())
    print(f"OK: {len(puu.taidot)} taitoa, {len(puu.roolit)} roolia, "
          f"{op} op.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
