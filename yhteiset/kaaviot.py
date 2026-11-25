#!/usr/bin/env python3
"""Tutoriaalien kaaviot: ajoituskaaviot ja Graphviz-kaaviot.

Käyttö:

    python3 yhteiset/kaaviot.py ajoitus  ULOS.pdf < kaavio.json
    python3 yhteiset/kaaviot.py dot      ULOS.pdf < kaavio.dot
    python3 yhteiset/kaaviot.py vcd SIMULAATIO.vcd --kello clk \\
        --signaalit valid,ready,data [--alku 0] [--jaksot 12] > kaavio.json

VCD-muuntimen muut valitsimet: --reuna laskeva, --naytteistys ennen
(arvo juuri ennen reunaa), --alkureuna (kello on 1 jo alussa),
--piilota-kello, --kanta h|d|s|b, --hscale ja --luettelo tila=LEPO:LUKU:KIRJ
(väylän arvot nimillä). Tuloste on sisennettyä JSONia, joten rivit
pysyvät lyhyinä.

Pandoc-suodatin kaaviot.lua kutsuu kahta ensimmäistä muotoa, kun
Markdownissa on koodilohko `.ajoituskaavio` tai `.dot`. Kolmas muoto
tuottaa ajoituskaavion simulaation VCD-tiedostosta, joten paketin testi
voi tarkistaa, että kirjassa näkyvä kaavio vastaa simulaatiota.

Ajoituskaavio kirjoitetaan WaveDromin JSON-muodon osajoukolla:

    {"signal": [
      {"name": "clk",   "wave": "p......"},
      {"name": "valid", "wave": "01..0.."},
      {"name": "data",  "wave": "x=.=x..", "data": ["A", "B"]},
      {},
      ["Väylä", {"name": "ready", "wave": "1.0.1.."}]
    ],
     "head": {"text": "Kättely"}, "config": {"hscale": 1}}

Aaltomerkit: 0 1 (vinot reunat), h l (suorat reunat), p n (kello
nousevalla tai laskevalla reunalla alkaen), P N (kello, jonka aktiivinen
reuna on merkitty nuolella), x (tuntematon), z (suuri impedanssi), = ja
2–9 (data, arvo `data`-luettelosta), . (edellinen jatkuu), | (katko).
Signaalilla voi olla `period` (jaksoa kohti merkin leveys).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# --- Värit ----------------------------------------------------------------

MUSTE = "#1F2A2E"
HILLITTY = "#5B6B70"
VIIVA = "#D9E0E3"
OLETUSKOROSTUS = "#0D7A6C"


def korostusvari() -> str:
    """Paketin alueen väri (ks. korostus.py); paketti on työhakemisto."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from korostus import korostus

        vari, _ = korostus(Path.cwd().name)
        return "#" + str(vari)
    except Exception:  # noqa: BLE001 - väri on vain ulkoasua
        return OLETUSKOROSTUS


def sekoita(vari: str, osuus: float) -> str:
    """Vaalentaa värin sekoittamalla sitä valkoiseen (osuus = värin osuus)."""
    r, g, b = (int(vari[i:i + 2], 16) for i in (1, 3, 5))
    def k(c: int) -> int:
        return round(c * osuus + 255 * (1 - osuus))
    return f"#{k(r):02X}{k(g):02X}{k(b):02X}"


# --- Ajoituskaavio --------------------------------------------------------

DATAMERKIT = set("=23456789")


def jaksot(aalto: str, period: int) -> list[str]:
    """Laajentaa aaltomerkkijonon jaksoiksi (yksi merkki jaksoa kohti)."""
    tulos: list[str] = []
    for m in aalto:
        tulos.append(m)
        tulos.extend(["."] * (period - 1))
    return tulos


def piirra_ajoitus(maaritys: dict[str, Any], ulos: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    from matplotlib.patches import Polygon, Rectangle

    perhe = "DejaVu Sans"
    mono = "DejaVu Sans Mono"
    nimet = {f.name for f in font_manager.fontManager.ttflist}
    if "Inter" in nimet:
        perhe = "Inter"
    # JetBrains Monon ligatuurit muuttaisivat nimen kuten "a |-> b"
    # nuolimerkiksi, joten signaalien nimissä käytetään DejaVu Sans Monoa.
    plt.rcParams.update({"font.family": perhe, "svg.hashsalt": "kaavio"})

    korostus = korostusvari()
    datavarit = [sekoita(korostus, 0.18), sekoita(korostus, 0.38),
                 sekoita("#B07A2A", 0.30), sekoita("#7A5BA8", 0.30),
                 sekoita("#3E7F3C", 0.30), sekoita("#B04848", 0.28),
                 sekoita("#2F5F9A", 0.30), sekoita("#8A7615", 0.30)]

    # Rivit: (ryhmän nimi tai None, signaali tai None välille).
    rivit: list[tuple[int, dict[str, Any] | None, str | None]] = []

    def kerää(lista: list[Any], taso: int) -> None:
        for s in lista:
            if isinstance(s, list):
                if s and isinstance(s[0], str):
                    rivit.append((taso, None, s[0]))
                    kerää(s[1:], taso + 1)
                else:
                    kerää(s, taso)
            elif isinstance(s, dict) and "wave" in s:
                rivit.append((taso, s, None))
            else:
                rivit.append((taso, None, ""))

    kerää(maaritys.get("signal", []), 0)
    if not rivit:
        raise SystemExit("kaaviot.py: ajoituskaaviossa ei ole signaaleja")

    hscale = float(maaritys.get("config", {}).get("hscale", 1))
    pituus = max(
        len(jaksot(s["wave"], int(s.get("period", 1))))
        for _, s, _ in rivit if s is not None)
    L = 1.0 * hscale           # jakson leveys
    K = 0.62                   # signaalin korkeus
    V = 0.20                   # reunan vinous (osuus jaksosta)
    nimileveys = max([len(str(s.get("name", ""))) for _, s, _ in rivit
                      if s is not None] + [len(r or "") for _, _, r in rivit
                                           if r]) * 0.16 + 0.5
    otsikko = maaritys.get("head", {}).get("text")
    yla = 0.6 if otsikko else 0.12
    ala = len(rivit) * 0.9 + 0.02
    korkeus = yla + ala
    leveys = nimileveys + pituus * L + 0.3
    skaala = 0.42              # tuumaa yksikköä kohti: 16 jaksoa ~ palsta
    fig = plt.figure(figsize=(leveys * skaala, korkeus * skaala))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(-nimileveys, pituus * L + 0.3)
    ax.set_ylim(-ala, yla)
    ax.axis("off")

    # Pystyviivat jaksojen rajoille.
    for i in range(pituus + 1):
        ax.plot([i * L, i * L], [0.1, -len(rivit) * 0.9 + 0.1],
                color=VIIVA, lw=0.5, zorder=0)
    if otsikko:
        ax.text(pituus * L / 2, 0.35, str(otsikko), ha="center", va="center",
                fontsize=9, fontweight="bold", color=MUSTE)

    vk: dict[str, Any] = {"color": MUSTE, "lw": 1.0,
                          "solid_capstyle": "butt", "zorder": 3}
    for rivi, (taso, s, ryhma) in enumerate(rivit):
        yk = -rivi * 0.9 - 0.45          # rivin keskikohta
        ya, yy = yk - K / 2, yk + K / 2  # ala- ja yläreuna
        if s is None:
            if ryhma:
                ax.text(-nimileveys + 0.1 + taso * 0.25, yk, ryhma,
                        ha="left", va="center", fontsize=8,
                        fontweight="bold", color=korostus)
            continue
        ax.text(-0.15, yk, str(s.get("name", "")), ha="right", va="center",
                fontsize=8, color=MUSTE, family=mono)
        period = int(s.get("period", 1))
        merkit = jaksot(s["wave"], period)
        data = [str(d) for d in s.get("data", [])]
        if isinstance(s.get("data"), str):
            data = s["data"].split()
        dataind = 0
        # Lohkot: (tila, alku, loppu, merkki)
        lohkot: list[list[Any]] = []
        for i, m in enumerate(merkit):
            if m == "." and lohkot:
                lohkot[-1][2] = i + 1
                continue
            if m == "|" and lohkot:
                lohkot[-1][2] = i + 1
                lohkot.append(["katko", i, i + 1, "|"])
                lohkot.append([lohkot[-2][0], i + 1, i + 1, lohkot[-2][3]])
                continue
            lohkot.append([m, i, i + 1, m])
        lohkot = [b for b in lohkot if b[2] > b[1] or b[0] == "katko"]
        edellinen_taso: float | None = None
        for b in lohkot:
            m, a, loppu = b[0], b[1] * L, b[2] * L
            if m == "katko":
                ax.add_patch(Rectangle((a + 0.3 * L, ya - 0.08), 0.4 * L,
                                       K + 0.16, color="white", zorder=5))
                for dx in (0.3, 0.7):
                    ax.plot([a + dx * L - 0.05, a + dx * L + 0.05],
                            [ya - 0.08, yy + 0.08], color=HILLITTY, lw=0.8,
                            zorder=6)
                continue
            if m in "pnPN":
                # Kellojakson pituus on signaalin period-arvo.
                P = L * period
                n = max(1, round((loppu - a) / P))
                for j in range(n):
                    x0 = a + j * P
                    eka, toka = (yy, ya) if m in "pP" else (ya, yy)
                    ax.plot([x0, x0, x0 + P / 2, x0 + P / 2, x0 + P],
                            [toka, eka, eka, toka, toka], **vk)
                    if m in "PN":
                        ax.annotate("", xy=(x0, yk + 0.12),
                                    xytext=(x0, yk - 0.12),
                                    arrowprops=dict(arrowstyle="-|>", lw=0.8,
                                                    color=korostus,
                                                    shrinkA=0, shrinkB=0),
                                    zorder=4)
                edellinen_taso = toka
                continue
            if m in "01hlHL":
                taso_y = yy if m in "1hH" else ya
                vino = V * L if m in "01" else 0.0
                if edellinen_taso is None or edellinen_taso == taso_y:
                    ax.plot([a, loppu], [taso_y, taso_y], **vk)
                else:
                    ax.plot([a, a + vino, loppu], [edellinen_taso, taso_y, taso_y],
                            **vk)
                edellinen_taso = taso_y
                continue
            # Väylät: data, x ja z.
            vino = V * L * 0.6
            if m == "z":
                if edellinen_taso is not None:
                    ax.plot([a, a + vino], [edellinen_taso, yk], **vk)
                ax.plot([a + vino if edellinen_taso is not None else a, loppu],
                        [yk, yk], color=HILLITTY, lw=1.0, zorder=3)
                edellinen_taso = yk
                continue
            if edellinen_taso is not None and edellinen_taso != yk:
                # Yksibittisestä väylään: viiva keskelle.
                ax.plot([a, a + vino], [edellinen_taso, yk], **vk)
            kulmat = [(a, yk), (a + vino, yy), (loppu - vino, yy), (loppu, yk),
                      (loppu - vino, ya), (a + vino, ya)]
            if m == "x":
                ax.add_patch(Polygon(kulmat, closed=True, facecolor="#EEF1F2",
                                     edgecolor=MUSTE, lw=1.0, hatch="////",
                                     zorder=2))
            else:
                vari = datavarit[0 if m == "=" else (int(m) - 2) % len(datavarit)]
                ax.add_patch(Polygon(kulmat, closed=True, facecolor=vari,
                                     edgecolor=MUSTE, lw=1.0, zorder=2))
                if dataind < len(data):
                    ax.text((a + loppu) / 2, yk, data[dataind], ha="center",
                            va="center", fontsize=7, family=mono, color=MUSTE,
                            zorder=4, clip_on=False)
                dataind += 1
            edellinen_taso = yk
    tallenna(fig, ulos)
    plt.close(fig)


def tallenna(fig: Any, ulos: str) -> None:
    pääte = Path(ulos).suffix.lower()
    if pääte == ".pdf":
        fig.savefig(ulos, metadata={"CreationDate": None, "Producer": None,
                                    "Creator": None})
    elif pääte == ".svg":
        fig.savefig(ulos, metadata={"Date": None, "Creator": None})
    else:
        fig.savefig(ulos, dpi=200, metadata={"Software": None})


# --- Graphviz ---------------------------------------------------------------

def piirra_dot(lahde: str, ulos: str) -> None:
    korostus = korostusvari()
    pääte = Path(ulos).suffix.lstrip(".").lower() or "pdf"
    perhe = "Inter"
    # Oletukset lisätään kaavion alkuun eikä komentoriville, jotta
    # kaavion omat graph/node/edge-rivit voivat ohittaa ne.
    oletukset = (
        f'graph [fontname="{perhe}", fontsize=10, color="{MUSTE}", '
        f'bgcolor="transparent"]; '
        f'node [fontname="{perhe}", fontsize=10, color="{MUSTE}", '
        f'style="rounded,filled", fillcolor="{sekoita(korostus, 0.12)}", '
        f'shape=box, penwidth=0.8]; '
        f'edge [fontname="{perhe}", fontsize=9, color="{HILLITTY}", '
        f'penwidth=0.8, arrowsize=0.6]; ')
    kohta = lahde.find("{")
    if kohta < 0:
        raise SystemExit("kaaviot.py: dot-kaaviossa ei ole aaltosulkua")
    lahde = lahde[:kohta + 1] + oletukset + lahde[kohta + 1:]
    args = ["dot", f"-T{pääte}", "-o", ulos]
    tulos = subprocess.run(args, input=lahde.encode("utf-8"),
                           capture_output=True, check=False)
    if tulos.returncode != 0:
        raise SystemExit("kaaviot.py: dot epäonnistui:\n" +
                         tulos.stderr.decode("utf-8", "replace"))
    if pääte == "pdf":
        poista_pdf_aikaleimat(ulos)


def poista_pdf_aikaleimat(polku: str) -> None:
    """Graphviz kirjoittaa PDF:ään luontiajan; poistetaan toistettavuuden vuoksi."""
    data = Path(polku).read_bytes()
    import re
    data = re.sub(rb"/CreationDate \(D:[^)]*\)", b"/CreationDate (D:20000101000000Z)",
                  data)
    Path(polku).write_bytes(data)


# --- VCD -> ajoituskaavio ------------------------------------------------------

def lue_vcd(polku: str) -> tuple[dict[str, tuple[str, int]], dict[str, list[tuple[int, str]]]]:
    """Palauttaa signaalien nimet (koko polku -> tunniste, leveys) ja
    muutokset tunnisteittain."""
    nimet: dict[str, tuple[str, int]] = {}
    muutokset: dict[str, list[tuple[int, str]]] = {}
    scope: list[str] = []
    aika = 0
    otsake = True
    with open(polku, encoding="utf-8", errors="replace") as f:
        sanat = f.read().split()
    i = 0
    while i < len(sanat):
        w = sanat[i]
        if otsake:
            if w == "$scope":
                scope.append(sanat[i + 2])
                i += 3
                while sanat[i] != "$end":
                    i += 1
            elif w == "$upscope":
                scope.pop()
                while sanat[i] != "$end":
                    i += 1
            elif w == "$var":
                leveys = int(sanat[i + 2])
                tunniste = sanat[i + 3]
                nimi = sanat[i + 4]
                koko = ".".join(scope + [nimi])
                nimet.setdefault(koko, (tunniste, leveys))
                muutokset.setdefault(tunniste, [])
                while sanat[i] != "$end":
                    i += 1
            elif w == "$enddefinitions":
                otsake = False
                while sanat[i] != "$end":
                    i += 1
            elif w.startswith("$"):
                while sanat[i] != "$end":
                    i += 1
            i += 1
            continue
        if w.startswith("#"):
            aika = int(w[1:])
        elif w in ("$dumpvars", "$end", "$dumpon", "$dumpoff", "$dumpall"):
            pass
        elif w[0] in "bBrR":
            arvo, tunniste = w[1:], sanat[i + 1]
            muutokset.setdefault(tunniste, []).append((aika, arvo.lower()))
            i += 1
        elif w[0] in "01xXzZuUwWlLhH-":
            muutokset.setdefault(w[1:], []).append((aika, w[0].lower()))
        i += 1
    return nimet, muutokset


def arvo_hetkella(lista: list[tuple[int, str]], t: int) -> str:
    arvo = "x"
    for aika, a in lista:
        if aika <= t:
            arvo = a
        else:
            break
    return arvo


def muotoile(arvo: str, leveys: int, kanta: str) -> str:
    # std_logic: heikot tasot l ja h luetaan nollaksi ja ykköseksi; u, w
    # ja - ovat tuntemattomia kuten x.
    arvo = arvo.replace("l", "0").replace("h", "1")
    muut = set(arvo) - {"0", "1"}
    if muut:
        return "z" if muut == {"z"} else "x"
    n = int(arvo, 2)
    if leveys == 1:
        return str(n)          # yksibittinen ei ole etumerkillinen luku
    if kanta == "d":
        return str(n)
    if kanta == "b":
        return f"{n:0{leveys}b}"
    if kanta == "s":
        # Kahden komplementti: ylin bitti on etumerkki.
        return str(n - (1 << leveys) if n >> (leveys - 1) else n)
    numerot = max(1, (leveys + 3) // 4)
    return f"{n:0{numerot}X}"


def vcd_kaavioksi(argv: list[str]) -> None:
    p = argparse.ArgumentParser(prog="kaaviot.py vcd")
    p.add_argument("vcd")
    p.add_argument("--kello", required=True, help="kellosignaalin nimi")
    p.add_argument("--signaalit", required=True,
                   help="pilkuin eroteltu luettelo; nimi=Näyttönimi "
                        "uudelleennimeää. Lyhyt nimi tarkoittaa ylimmän tason "
                        "signaalia; syvemmällä olevasta annetaan polun "
                        "loppuosa (esim. u_dut.valid). Moniselitteinen nimi "
                        "on virhe.")
    p.add_argument("--alku", type=int, default=0,
                   help="ensimmäinen näytettävä kellojakso (nousevat reunat)")
    p.add_argument("--jaksot", type=int, default=12)
    p.add_argument("--kanta", choices=["h", "d", "s", "b"], default="h",
                   help="väylien arvot heksana (h), kymmenjärjestelmässä (d), "
                        "etumerkillisinä (s) tai binäärinä (b)")
    p.add_argument("--hscale", type=float,
                   help="jakson leveyskerroin kaaviossa (config.hscale)")
    p.add_argument("--reuna", choices=["nouseva", "laskeva"],
                   default="nouseva", help="näytteistävä kellon reuna")
    p.add_argument("--piilota-kello", action="store_true",
                   help="näytteistyskelloa ei piirretä kaavioon")
    p.add_argument("--luettelo", action="append", default=[],
                   metavar="SIGNAALI=NIMI0:NIMI1:...",
                   help="näyttää väylän arvot nimillä (luettelotyyppi)")
    p.add_argument("--otsikko")
    p.add_argument("--naytteistys", choices=["jalkeen", "ennen"],
                   default="jalkeen",
                   help="arvo kellon nousevan reunan jälkeen (oletus) tai "
                        "juuri ennen sitä")
    p.add_argument("--alkureuna", action="store_true",
                   help="lasketaan nousevaksi reunaksi myös kellon arvo 1 "
                        "simulaation alussa (esim. yosys-smtbmc:n jäljet)")
    a = p.parse_args(argv)
    nimet, muutokset = lue_vcd(a.vcd)

    def hae(nimi: str) -> tuple[str, int]:
        if nimi in nimet:
            return nimet[nimi]
        osumat = [k for k in nimet if k.endswith("." + nimi)]
        if not osumat:
            raise SystemExit(f"kaaviot.py: signaalia {nimi!r} ei löydy VCD:stä")
        # Lyhyt nimi tarkoittaa ensisijaisesti ylimmän tason (testipenkin)
        # omaa signaalia, jos siellä on täsmälleen yksi sen niminen.
        ylin = min(k.count(".") for k in nimet)
        ylimmat = [k for k in osumat if k.count(".") == ylin]
        if len(ylimmat) == 1:
            return nimet[ylimmat[0]]
        # Muuten sama johdin näkyy usein monella hierarkiatasolla (portti
        # ja siihen kytketty signaali). Lyhyt nimi kelpaa, jos kaikki
        # osumat ovat sama johdin tai niiden aaltomuoto on täsmälleen sama.
        eka = nimet[osumat[0]]
        for k in osumat[1:]:
            t, lev = nimet[k]
            if t != eka[0] and (lev != eka[1]
                                or muutokset[t] != muutokset[eka[0]]):
                raise SystemExit(f"kaaviot.py: nimi {nimi!r} on moniselitteinen "
                                 f"(eri signaaleja): {osumat}; anna polun "
                                 "loppuosa, esim. dut." + nimi)
        return eka

    kt, _ = hae(a.kello)
    uusi, vanha = ("1", "0") if a.reuna == "nouseva" else ("0", "1")
    nousut = [t for (t, v), (_, ed) in zip(muutokset[kt][1:], muutokset[kt])
              if v == uusi and ed == vanha]
    if a.alkureuna and muutokset[kt] and muutokset[kt][0][1] == uusi:
        nousut.insert(0, muutokset[kt][0][0])
    if len(nousut) < a.alku + a.jaksot:
        raise SystemExit("kaaviot.py: VCD:ssä on liian vähän kellojaksoja")
    hetket = nousut[a.alku:a.alku + a.jaksot]
    signaalit: list[dict[str, Any]] = []
    if not a.piilota_kello:
        signaalit.append({"name": a.kello.split(".")[-1],
                          "wave": ("p" if a.reuna == "nouseva" else "n")
                          + "." * (a.jaksot - 1)})
    luettelot: dict[str, list[str]] = {}
    for maare in a.luettelo:
        nimi, _, arvot = maare.partition("=")
        luettelot[nimi] = arvot.split(":")
    for maare in a.signaalit.split(","):
        nimi, _, naytto = maare.partition("=")
        tunniste, leveys = hae(nimi)
        aalto = ""
        data: list[str] = []
        edellinen = None
        for t in hetket:
            # Arvo kellon nousun jälkeen (rekisteröity arvo näkyy jaksolla).
            hetki = t - 1 if a.naytteistys == "ennen" else t
            raaka = arvo_hetkella(muutokset[tunniste], hetki)
            arvo = muotoile(raaka, leveys, a.kanta)
            if nimi in luettelot and arvo not in ("x", "z"):
                n = int(raaka, 2)
                arvo = luettelot[nimi][n] if n < len(luettelot[nimi]) else arvo
            if arvo == edellinen:
                aalto += "."
            elif leveys == 1 or arvo in ("x", "z"):
                aalto += arvo
            else:
                aalto += "="
                data.append(arvo)
            edellinen = arvo
        s: dict[str, Any] = {"name": naytto or nimi.split(".")[-1], "wave": aalto}
        if data:
            s["data"] = data
        signaalit.append(s)
    tulos: dict[str, Any] = {"signal": signaalit}
    if a.otsikko:
        tulos["head"] = {"text": a.otsikko}
    if a.hscale:
        tulos["config"] = {"hscale": a.hscale}
    # Sama muoto kuin `python3 -m json.tool --indent 1`: rivit pysyvät
    # lyhyinä, joten tiedoston voi näyttää kirjassa sellaisenaan.
    json.dump(tulos, sys.stdout, indent=1)
    sys.stdout.write("\n")


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ("ajoitus", "dot", "vcd"):
        raise SystemExit(__doc__)
    laji = sys.argv[1]
    if laji == "vcd":
        vcd_kaavioksi(sys.argv[2:])
        return
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    ulos = sys.argv[2]
    lahde = sys.stdin.read()
    os.makedirs(os.path.dirname(os.path.abspath(ulos)), exist_ok=True)
    if laji == "ajoitus":
        try:
            maaritys = json.loads(lahde)
        except json.JSONDecodeError as e:
            raise SystemExit(f"kaaviot.py: ajoituskaavio ei ole JSONia: {e}")
        piirra_ajoitus(maaritys, ulos)
    else:
        piirra_dot(lahde, ulos)


if __name__ == "__main__":
    main()
