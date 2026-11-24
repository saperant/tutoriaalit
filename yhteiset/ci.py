#!/usr/bin/env python3
"""CI:n apuvälineet: muuttuneet paketit ja PDF-välimuisti.

Käyttö:

    python3 yhteiset/ci.py muuttuneet [--perusta SHA]
        Tulostaa kaksi riviä GitHub Actionsin tulosteiksi:
          paketit=<välilyönnein eroteltu luettelo tai "kaikki">
          kontit=<JSON-luettelo kehityskonteista>
        Perusta on viimeisin commit, jonka CI-ajo onnistui. Jos sitä ei
        anneta tai se ei ole saatavilla, tai jos muutos koskee yhteisiä
        tiedostoja (yhteiset/, juuren Makefile, CI, kehityskonttien
        Dockerfile), testataan kaikki.

    python3 yhteiset/ci.py pdf-palauta HAKEMISTO
    python3 yhteiset/ci.py pdf-tallenna HAKEMISTO
        Palauttaa välimuistista ne PDF:t, joiden lähteet eivät ole
        muuttuneet, ja tallentaa rakennetut PDF:t välimuistiin. Paketin
        tunniste on Gitin puutiiviste paketin hakemistosta, yhteiset/-
        hakemistosta ja taitopuusta (PDF:n väri ja alue tulevat siitä),
        joten mikä tahansa muutos lähteissä rakentaa PDF:n uudelleen.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

JUURI = Path(__file__).resolve().parent.parent

# Polut, joiden muutos voi vaikuttaa kaikkiin paketteihin.
YHTEISET = ("yhteiset/", "Makefile", ".github/", ".devcontainer/Dockerfile")
# Nämä testataan aina: taitopuu ja sivusto kokoavat kaikki paketit.
AINA = ("opintopolut", "sivusto")


def git(*args: str) -> str:
    tulos = subprocess.run(["git", "-C", str(JUURI), *args],
                           capture_output=True, text=True, check=False)
    if tulos.returncode != 0:
        raise RuntimeError(tulos.stderr.strip())
    return tulos.stdout.strip()


def paketit() -> list[str]:
    """Hakemistot, joissa on Makefile (sivusto viimeisenä, kuten juuressa)."""
    nimet = sorted(p.parent.name for p in JUURI.glob("*/Makefile"))
    return [n for n in nimet if n != "sivusto"] + (
        ["sivusto"] if "sivusto" in nimet else [])


def kehityskontit() -> list[str]:
    tulos = subprocess.run(
        [sys.executable, str(JUURI / "yhteiset" / "testaa_kontti.py"), "--lista"],
        capture_output=True, text=True, check=True)
    lista: list[str] = json.loads(tulos.stdout)
    return lista


def muuttuneet(argv: list[str]) -> None:
    perusta = ""
    if len(argv) >= 2 and argv[0] == "--perusta":
        perusta = argv[1]
    kaikki = False
    tiedostot: list[str] = []
    if not perusta:
        kaikki = True
    else:
        try:
            tiedostot = git("diff", "--name-only", f"{perusta}...HEAD").splitlines()
        except RuntimeError:
            kaikki = True
    if any(t.startswith(YHTEISET) or t in YHTEISET for t in tiedostot):
        kaikki = True

    if kaikki:
        print("paketit=kaikki")
        print("kontit=" + json.dumps(kehityskontit()))
        return

    olemassa = set(paketit())
    muuttui: set[str] = set()
    for t in tiedostot:
        osat = t.split("/")
        if osat[0] == ".devcontainer" and len(osat) > 2:
            muuttui.add(osat[1])
        elif len(osat) > 1:
            muuttui.add(osat[0])
    testattavat = [p for p in paketit() if p in muuttui or p in AINA]
    testattavat = [p for p in testattavat if p in olemassa]
    kontit = [k for k in kehityskontit() if k in muuttui]
    print("paketit=" + " ".join(testattavat))
    print("kontit=" + json.dumps(kontit))


def tunniste(paketti: str) -> str:
    osat = [git("rev-parse", f"HEAD:{paketti}"),
            git("rev-parse", "HEAD:yhteiset"),
            git("rev-parse", "HEAD:opintopolut/taitopuu.toml")]
    return "-".join(osat)


def pdf_tiedostot(paketti: str) -> list[Path]:
    return sorted((JUURI / paketti).glob("*.pdf"))


def pdf_palauta(hakemisto: Path) -> None:
    luettelo = hakemisto / "luettelo.json"
    if not luettelo.exists():
        print("PDF-välimuisti on tyhjä.")
        return
    tiedot: dict[str, str] = json.loads(luettelo.read_text("utf-8"))
    palautettu = 0
    for paketti in paketit():
        try:
            t = tunniste(paketti)
        except RuntimeError:
            continue  # hakemisto ei ole versionhallinnassa
        if tiedot.get(paketti) != t:
            continue
        lahde = hakemisto / paketti
        if not lahde.is_dir():
            continue
        for pdf in lahde.glob("*.pdf"):
            kohde = JUURI / paketti / pdf.name
            shutil.copyfile(pdf, kohde)
            kohde.touch()  # uudempi kuin lähteet, joten make ei rakenna
        palautettu += 1
    print(f"PDF-välimuistista palautettiin {palautettu} paketin PDF:t.")


def pdf_tallenna(hakemisto: Path) -> None:
    if hakemisto.exists():
        shutil.rmtree(hakemisto)
    hakemisto.mkdir(parents=True)
    tiedot: dict[str, str] = {}
    for paketti in paketit():
        pdf = pdf_tiedostot(paketti)
        if not pdf:
            continue
        try:
            tiedot[paketti] = tunniste(paketti)
        except RuntimeError:
            continue
        (hakemisto / paketti).mkdir()
        for p in pdf:
            shutil.copyfile(p, hakemisto / paketti / p.name)
    (hakemisto / "luettelo.json").write_text(
        json.dumps(tiedot, indent=1, sort_keys=True) + "\n", "utf-8")
    print(f"PDF-välimuistiin tallennettiin {len(tiedot)} paketin PDF:t.")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    komento, argv = sys.argv[1], sys.argv[2:]
    if komento == "muuttuneet":
        muuttuneet(argv)
    elif komento == "pdf-palauta" and len(argv) == 1:
        pdf_palauta(Path(argv[0]))
    elif komento == "pdf-tallenna" and len(argv) == 1:
        pdf_tallenna(Path(argv[0]))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
