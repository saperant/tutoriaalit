#!/usr/bin/env python3
"""Tuottaa kirjan commit-verkkojen kaaviot esimerkkien repositorioista.

Käyttö:  python3 kaaviot/tee.py            kirjoittaa kaaviot/*.dot
         python3 kaaviot/tee.py --tarkista  vertaa tallennettuihin

Jokainen kaavio syntyy näin: testattu esimerkkiskripti ajetaan tyhjässä
hakemistossa alusta nimettyyn riviin asti, ja syntyneestä repositoriosta
luetaan commitit, niiden vanhemmat ja viitteet Gitin omilla komennoilla.
Kaavion tunnisteet ja viestit ovat siis samat kuin esimerkin
tulosteessa, ja kaavio muuttuu, jos esimerkki muuttuu.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

JUURI = Path(__file__).resolve().parent.parent
YMPARISTO = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null",
             "GIT_CONFIG_NOSYSTEM": "1", "LC_ALL": "C.UTF-8"}
VIITE = 'shape=box, style="filled", fillcolor="#FBEFD5", margin="0.08,0.03"'
VANHA = ('style="rounded,dashed", color="#9AA7AB", fontcolor="#7A888C", '
         'fillcolor="#FFFFFF"')


@dataclass
class Tila:
    """Yhden repositorion commitit ja viitteet."""
    commitit: list[tuple[str, list[str], str]]   # tunniste, vanhemmat, viesti
    elavat: set[str]                             # viitteistä saavutettavat
    viitteet: list[tuple[str, str]]              # nimi, tunniste
    head: str                                    # haaran nimi tai tunniste
    korostus: dict[str, str] = field(default_factory=dict)


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True,
                          env=YMPARISTO).stdout


def aja(esimerkki: str, loppu: str) -> Path:
    """Ajaa esimerkin alun riviin asti, jolla teksti `loppu` on."""
    rivit = (JUURI / "esimerkit" / esimerkki).read_text("utf-8").splitlines()
    for i, rivi in enumerate(rivit):
        if loppu in rivi:
            break
    else:
        raise SystemExit(f"tee.py: {esimerkki}: riviä '{loppu}' ei löydy")
    tmp = Path(tempfile.mkdtemp(prefix="kaavio-"))
    subprocess.run(["bash", "-c", "\n".join(rivit[:i + 1])], cwd=tmp,
                   check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, env=YMPARISTO)
    return tmp


def lue(repo: Path) -> Tila:
    """Lukee repositorion verkon; reflogin kautta myös hylätyt commitit."""
    commitit = []
    loki = git(repo, "log", "--all", "--reflog", "--topo-order", "--reverse",
               "--format=%h%x09%p%x09%s", "HEAD")
    for rivi in loki.splitlines():
        tunniste, vanhemmat, viesti = rivi.split("\t")
        commitit.append((tunniste, vanhemmat.split(), viesti))
    elavat = set(git(repo, "rev-list", "--abbrev-commit", "--all",
                     "HEAD").split())
    viitteet = []
    for rivi in git(repo, "for-each-ref", "refs/heads", "refs/remotes",
                    "--format=%(refname:short)%09%(objectname:short)"
                    ).splitlines():
        nimi, tunniste = rivi.split("\t")
        if nimi not in ("origin", "origin/HEAD"):
            viitteet.append((nimi, tunniste))
    haara = subprocess.run(
        ["git", "-C", str(repo), "symbolic-ref", "-q", "--short", "HEAD"],
        capture_output=True, text=True, env=YMPARISTO).stdout.strip()
    head = haara or git(repo, "rev-parse", "--short", "HEAD").strip()
    return Tila(commitit, elavat, viitteet, head)


def tila(esimerkki: str, loppu: str, *hakemistot: str) -> list[Tila]:
    tmp = aja(esimerkki, loppu)
    try:
        return [lue(tmp / h) for h in hakemistot]
    finally:
        shutil.rmtree(tmp)


def lainaa(teksti: str) -> str:
    return teksti.replace("\\", "\\\\").replace('"', '\\"')


def verkko(t: Tila, e: str, head: bool = True) -> list[str]:
    """Yhden repositorion solmut ja kaaret; `e` on solmujen etuliite."""
    r = []
    for tunniste, _, viesti in t.commitit:
        nimi, lisa = lainaa(viesti), ""
        if tunniste not in t.elavat:
            lisa = ", " + VANHA
        elif tunniste in t.korostus:
            nimi += f"\\n({t.korostus[tunniste]})"
            lisa = ", penwidth=2.2"
        r.append(f'  {e}{tunniste} [label="{tunniste}\\n{nimi}"{lisa}];')
    for tunniste, vanhemmat, _ in t.commitit:
        for v in vanhemmat:
            tyyli = "" if tunniste in t.elavat else ', color="#9AA7AB"'
            r.append(f"  {e}{v} -> {e}{tunniste} [dir=back{tyyli}];")
    # Samaan committiin osoittavat viitteet kootaan yhteen lappuun.
    laput: dict[str, list[str]] = {}
    for nimi, tunniste in t.viitteet:
        on_head = head and nimi == t.head
        laput.setdefault(tunniste, []).append(
            f"HEAD → {nimi}" if on_head else nimi)
    if head and all(nimi != t.head for nimi, _ in t.viitteet):
        laput.setdefault(t.head, []).append("HEAD (irrallinen)")
    for tunniste, nimet in laput.items():
        nimet.sort(key=lambda n: not n.startswith("HEAD"))
        teksti = "\\n".join(nimet)
        r.append(f'  {e}v{tunniste} [label="{teksti}", {VIITE}];')
        r.append(f"  {{rank=same; {e}{tunniste} -> {e}v{tunniste} "
                 "[dir=back];}")
    return r


def kaavio(osat: list[tuple[str, Tila]], head: bool = True) -> str:
    """Tilat rinnakkain omissa kehyksissään, vanhin commit ylimpänä."""
    r = ["digraph {", "  nodesep=0.25; ranksep=0.3;",
         '  node [margin="0.1,0.05"];']
    for i, (otsikko, t) in enumerate(osat):
        if not otsikko:                 # yksi tila: ei kehystä
            r += verkko(t, f"k{i}_", head)
            continue
        r.append(f"  subgraph cluster_{i} {{")
        r.append(f'    label="{lainaa(otsikko)}"; color="#D9E0E3";')
        r += ["  " + rivi for rivi in verkko(t, f"k{i}_", head)]
        r.append("  }")
    r.append("}")
    return "\n".join(r) + "\n"


def oliot() -> str:
    """02-tilannekuvat: commitit, puut ja blobit; jaetut blobit näkyvät."""
    tmp = aja("02-tilannekuvat.sh", "# @loppu nimeaminen")
    repo = tmp / "laskuri"
    try:
        r = ["digraph {", "  nodesep=0.3; ranksep=0.45;"]
        commitit, puut, blobit, kaaret = [], [], [], []
        loki = git(repo, "log", "--reverse", "--format=%h%x09%p%x09%t%x09%s")
        for rivi in loki.splitlines():
            c, vanhempi, puu, viesti = rivi.split("\t")
            commitit.append(c)
            r.append(f'  c{c} [label="commit {c}\\n{lainaa(viesti)}"];')
            if vanhempi:
                kaaret.append(f"  c{vanhempi} -> c{c} "
                              '[dir=back, label="vanhempi"];')
            puut.append(puu)
            r.append(f'  t{puu} [label="tree {puu}", shape=folder, '
                     'style="filled", fillcolor="#EEF2F4"];')
            kaaret.append(f"  c{c} -> t{puu};")
            for kohde in git(repo, "ls-tree", "--abbrev=7", puu).splitlines():
                tiedot, nimi = kohde.split("\t")
                blob = tiedot.split()[2]
                if blob not in blobit:
                    blobit.append(blob)
                    r.append(f'  b{blob} [label="blob {blob}", shape=note, '
                             'style="filled", fillcolor="#FFFFFF"];')
                kaaret.append(f'  t{puu} -> b{blob} [label="{nimi}"];')
        r.append("  {rank=same; " + " ".join(f"c{c};" for c in commitit) + "}")
        r.append("  {rank=same; " + " ".join(f"t{t};" for t in puut) + "}")
        r.append("  {rank=same; " + " ".join(f"b{b};" for b in blobit) + "}")
        return "\n".join(r + kaaret + ["}"]) + "\n"
    finally:
        shutil.rmtree(tmp)


def viitteet() -> str:
    (t,) = tila("02-tilannekuvat.sh", "# @loppu nimeaminen", "laskuri")
    return kaavio([("", t)])


def pikakelaus() -> str:
    (ennen,) = tila("04-haarat.sh", "# @loppu haara", "laskuri")
    (jalkeen,) = tila("04-haarat.sh", "git merge --ff-only sanat", "laskuri")
    return kaavio([("ennen", ennen),
                   ("git merge --ff-only sanat", jalkeen)])


def yhdistaminen() -> str:
    tmp = aja("04-yhdistaminen.sh", "# @loppu erkaantuminen")
    try:
        ennen = lue(tmp / "laskuri")
        kanta = git(tmp / "laskuri", "merge-base", "main", "sanat")[:7]
    finally:
        shutil.rmtree(tmp)
    ennen.korostus[kanta] = "yhteinen kanta"
    (jalkeen,) = tila("04-yhdistaminen.sh", "# @loppu yhdistaminen",
                      "laskuri")
    return kaavio([("ennen", ennen), ("git merge sanat", jalkeen)])


def rebase() -> str:
    (ennen,) = tila("06-rebase.sh", "# @loppu ennen", "laskuri")
    (jalkeen,) = tila("06-rebase.sh", "git rebase -q main", "laskuri")
    return kaavio([("ennen", ennen), ("git rebase main", jalkeen)])


def etarepot(esimerkki: str, loppu: str) -> str:
    palvelin, aino, olli = tila(esimerkki, loppu, "laskuri.git", "aino",
                                "olli")
    return kaavio([("Aino", aino), ("palvelin", palvelin),
                   ("Olli", olli)], head=False)


def haku() -> str:
    (ennen,) = tila("07-eta.sh", "# @loppu olli-tyo", "aino")
    (haettu,) = tila("07-eta.sh", "git fetch -q", "aino")
    (yhdistetty,) = tila("07-eta.sh", "git merge -q --ff-only origin/main",
                         "aino")
    return kaavio([("ennen", ennen), ("git fetch", haettu),
                   ("git merge --ff-only origin/main", yhdistetty)])


KAAVIOT = {
    "02-oliot.dot": oliot,
    "02-viitteet.dot": viitteet,
    "04-pikakelaus.dot": pikakelaus,
    "04-yhdistaminen.dot": yhdistaminen,
    "06-rebase.dot": rebase,
    "07-kolme-repoa.dot": lambda: etarepot("07-eta.sh", "# @loppu olli-tyo"),
    "07-haku.dot": haku,
    "07-hylatty.dot": lambda: etarepot("07-ristiriita.sh",
                                       "# @loppu hylatty"),
}


def main() -> None:
    tarkista = "--tarkista" in sys.argv
    virheita = 0
    for nimi, tee in KAAVIOT.items():
        polku = JUURI / "kaaviot" / nimi
        uusi = tee()
        if not tarkista:
            polku.write_text(uusi, "utf-8")
        elif not polku.exists() or polku.read_text("utf-8") != uusi:
            print(f"VIRHE: kaaviot/{nimi} ei vastaa esimerkin repositoriota "
                  "(aja python3 kaaviot/tee.py)")
            virheita += 1
    if tarkista and not virheita:
        print(f"OK: {len(KAAVIOT)} kaaviota vastaa esimerkkien "
              "repositorioita")
    sys.exit(1 if virheita else 0)


if __name__ == "__main__":
    main()
