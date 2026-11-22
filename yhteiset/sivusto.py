#!/usr/bin/env python3
"""Taitopuukartan verkkosivuston rakentaja.

Käyttö:  sivusto.py <repositorion juuri> <lähdehakemisto> <kohdehakemisto>

Lukee taitopuun (opintopolut/taitopuu.toml), laskee kartan asettelun ja
kirjoittaa kohdehakemistoon:

  index.html          kokonainen sivu (GitHub Pages)
  artefakti.html      sama sivu ilman HTML-runkoa (esikatselu)
  taitopuu.json       kartan data: taidot, sijainnit, reitit, materiaalit
  kartta.css, kartta.js
  materiaalit/        tutoriaalien PDF:t ja esimerkkipaketit (zip), joissa
                      on mukana devcontainer-konfiguraatio
"""

from __future__ import annotations

import datetime
import json
import math
import shutil
import sys
import tomllib
import zipfile
from pathlib import Path

import asettelu
import taitopuu as tp

ZIP_AIKA = (2026, 1, 1, 0, 0, 0)
RUNKO_ALKU = """<!doctype html>
<html lang="fi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
"""


def lukujen_otsikot(hakemisto: Path) -> list[str]:
    otsikot = []
    for md in sorted((hakemisto / "luvut").glob("*.md")):
        for rivi in md.read_text("utf-8").splitlines():
            if rivi.startswith("# "):
                otsikot.append(rivi[2:].strip())
                break
    return otsikot


def esimerkkipaketti(juuri: Path, tutoriaali: str, kohde: Path) -> bool:
    """Pakkaa tutoriaalin esimerkit ja devcontainer-konfiguraation."""
    esimerkit = juuri / tutoriaali / "esimerkit"
    konfiguraatio = juuri / ".devcontainer" / tutoriaali / "devcontainer.json"
    if not esimerkit.is_dir() or not konfiguraatio.exists():
        return False

    asetukset = json.loads(konfiguraatio.read_text("utf-8"))
    asetukset["build"] = {"dockerfile": "Dockerfile", "context": ".",
                          "args": asetukset.get("build", {}).get("args", {})}
    asetukset.pop("workspaceFolder", None)

    juurikansio = f"{tutoriaali}-esimerkit"
    ohje = (f"# {tutoriaali}: esimerkit\n\n"
            "Tutoriaalin testatut esimerkkiohjelmat.\n\n"
            "## Käyttö kehityskontissa\n\n"
            "Avaa kansio Visual Studio Codessa ja valitse *Dev Containers: "
            "Reopen in Container*. Kontissa on valmiina kääntäjät ja "
            "debuggeri, ja esimerkit käännetään automaattisesti.\n\n"
            "## Käyttö ilman konttia\n\n"
            "```text\n"
            "make            # kääntää kaikki esimerkit hakemistoon bin/\n"
            "make aja-01-hei # kääntää ja ajaa yhden esimerkin\n"
            "```\n\n"
            "Lisenssi: CC BY-SA 4.0.\n")

    kohde.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(kohde, "w", zipfile.ZIP_DEFLATED) as z:
        def lisaa(nimi: str, data: bytes):
            tieto = zipfile.ZipInfo(f"{juurikansio}/{nimi}", ZIP_AIKA)
            tieto.external_attr = 0o644 << 16
            tieto.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(tieto, data)

        for polku in sorted(esimerkit.rglob("*")):
            if polku.is_file() and "bin" not in polku.relative_to(
                    esimerkit).parts:
                lisaa(polku.relative_to(esimerkit).as_posix(),
                      polku.read_bytes())
        lisaa(".devcontainer/devcontainer.json",
              (json.dumps(asetukset, ensure_ascii=False, indent=2)
               + "\n").encode("utf-8"))
        lisaa(".devcontainer/Dockerfile",
              (juuri / ".devcontainer" / "Dockerfile").read_bytes())
        lisaa("README.md", ohje.encode("utf-8"))
    return True


def rakenna_data(juuri: Path, kohde: Path) -> dict:
    toml = juuri / "opintopolut" / "taitopuu.toml"
    puu, virheet = tp.lataa(toml)
    if virheet:
        sys.exit("taitopuu ei ole eheä:\n" + "\n".join(virheet))
    asetukset = tomllib.loads(toml.read_text("utf-8")).get("sivusto", {})
    repo = asetukset["repo"]
    haara = asetukset.get("haara", "main")

    sijainnit, keskukset = asettelu.aseta(puu)
    reitit = asettelu.reitit(puu, sijainnit)
    materiaalit = kohde / "materiaalit"
    materiaalit.mkdir(parents=True, exist_ok=True)

    taidot = []
    for t in puu.taidot.values():
        aineisto = None
        if t.valmis:
            d = t.tutoriaali
            aineisto = {
                "lahde": f"https://github.com/{repo}/tree/{haara}/{d}",
                "luvut": lukujen_otsikot(juuri / d),
            }
            pdf = juuri / d / f"{d}.pdf"
            if pdf.exists():
                shutil.copy(pdf, materiaalit / pdf.name)
                aineisto["pdf"] = f"materiaalit/{pdf.name}"
            paketti = materiaalit / f"{d}-esimerkit.zip"
            if esimerkkipaketti(juuri, d, paketti):
                aineisto["esimerkit"] = f"materiaalit/{paketti.name}"
                aineisto["codespaces"] = (
                    f"https://codespaces.new/{repo}?devcontainer_path="
                    f".devcontainer/{d}/devcontainer.json")
        x, y = sijainnit[t.id]
        taidot.append({
            "id": t.id, "nimi": t.nimi, "alue": t.alue,
            "kuvaus": t.kuvaus, "edellyttaa": t.edellyttaa,
            "seuraajat": sorted(t.seuraajat), "aiheet": t.aiheet,
            "laajuus": t.laajuus, "taso": t.taso, "testaus": t.testaus,
            "roadmap": t.roadmap, "amk": t.amk, "x": x, "y": y,
            "materiaalit": aineisto,
        })

    opintopolut_pdf = juuri / "opintopolut" / "opintopolut.pdf"
    if opintopolut_pdf.exists():
        shutil.copy(opintopolut_pdf, materiaalit / opintopolut_pdf.name)

    alueet = []
    ulkokeha = asettelu.sade(max(t.taso for t in puu.taidot.values()))
    for i, (aid, a) in enumerate(puu.alueet.items()):
        nimike = None
        if aid in keskukset:
            # Aluenimi alueen taitojen suuntaan, uloimman taidon taakse.
            omat = [t for t in puu.taidot.values() if t.alue == aid]
            kulma = asettelu.keskikulma(
                [(math.atan2(sijainnit[t.id][1], sijainnit[t.id][0]), 1.0)
                 for t in omat])
            r = max(asettelu.sade(t.taso) for t in omat) + 125
            nimike = {"x": round(r * math.cos(kulma), 1),
                      "y": round(r * math.sin(kulma), 1)}
        alueet.append({"id": aid, "nimi": a["nimi"], "kuvaus": a["kuvaus"],
                       "indeksi": i, "nimike": nimike})
    return {
        "meta": {
            "repo": f"https://github.com/{repo}",
            "generoitu": datetime.date.today().isoformat(),
            "kehat": [asettelu.sade(k) for k in
                      range(1, max(t.taso for t in puu.taidot.values()) + 1)],
            "ulkokeha": ulkokeha,
            "opintopolut_pdf": ("materiaalit/opintopolut.pdf"
                                if opintopolut_pdf.exists() else None),
            "roadmap_haettu": puu.lahteet.get("roadmap_haettu"),
        },
        "alueet": alueet,
        "taidot": taidot,
        "roolit": [{"id": r.id, "nimi": r.nimi, "kuvaus": r.kuvaus,
                    "tavoitteet": r.tavoitteet,
                    "valinnaiset": r.valinnaiset}
                   for r in puu.roolit.values()],
        "reitit": reitit,
    }


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    juuri, lahde, kohde = (Path(a).resolve() for a in sys.argv[1:])
    if kohde.exists():
        shutil.rmtree(kohde)
    kohde.mkdir(parents=True)

    data = rakenna_data(juuri, kohde)
    (kohde / "taitopuu.json").write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")), "utf-8")
    for nimi in ("kartta.css", "kartta.js"):
        shutil.copy(lahde / nimi, kohde / nimi)

    sivu = (lahde / "kartta.html").read_text("utf-8")
    paa, merkki, runko = sivu.partition("<!-- runko -->")
    if not merkki:
        sys.exit("kartta.html: merkintä <!-- runko --> puuttuu")
    (kohde / "artefakti.html").write_text(sivu, "utf-8")
    (kohde / "index.html").write_text(
        RUNKO_ALKU + paa.strip() + "\n</head>\n<body>\n" + runko.strip()
        + "\n</body>\n</html>\n", "utf-8")

    valmiit = sum(1 for t in data["taidot"] if t["materiaalit"])
    print(f"Sivusto: {kohde} ({len(data['taidot'])} taitoa, "
          f"{valmiit} valmista materiaalia)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
