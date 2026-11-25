"""Tutoriaalikokoelman kehityskontit: säännöt ja paketin työkalut.

Käyttö:  python3 kokoelma.py                    tarkistaa kaikki
         python3 kokoelma.py tyokalut PAKETTI   paketin työkalut

Etsii repositorion juuren ja lukee tiedostot
.devcontainer/<paketti>/devcontainer.json. Tarkistuksen tulosteessa on
vain kaikkia koskevat säännöt, joten se ei muutu, kun paketteja lisätään.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from devkontti import Asetukset, lue_jsonc, tarkista


def repositorion_juuri() -> Path | None:
    for hakemisto in Path(__file__).resolve().parents:
        if (hakemisto / ".devcontainer" / "Dockerfile").is_file() \
                and (hakemisto / "yhteiset").is_dir():
            return hakemisto
    return None


# @alku saannot
def dockerfilen_argumentit(dockerfile: Path) -> set[str]:
    return set(re.findall(r"^ARG (\w+)", dockerfile.read_text("utf-8"),
                          re.MULTILINE))


def saannot(juuri: Path, paketti: str, a: Asetukset) -> dict[str, bool]:
    """Säännöt, jotka pätevät kokoelman jokaiseen kehityskonttiin."""
    rakennus = a.get("build", {})
    juuressa = "/workspaces/${localWorkspaceFolderBasename}"
    esimerkeissa = f"{juuressa}/{paketti}/esimerkit"
    onko_esimerkit = (juuri / paketti / "esimerkit").is_dir()
    sallitut = dockerfilen_argumentit(juuri / ".devcontainer" / "Dockerfile")
    return {
        "nimi kertoo paketin (name)": bool(a.get("name")),
        "yhteinen Dockerfile (build.dockerfile)":
            rakennus.get("dockerfile") == "../Dockerfile"
            and rakennus.get("context") == "..",
        "rakennusargumentit ovat Dockerfilen tuntemia":
            set(rakennus.get("args", {})) <= sallitut,
        "avautuu paketin esimerkkeihin (workspaceFolder)":
            a.get("workspaceFolder") == esimerkeissa
            or (not onko_esimerkit and a.get("workspaceFolder") == juuressa),
        "läpäisee tarkistimen": not tarkista(a),
    }
# @loppu saannot


def tarkista_kaikki(juuri: Path) -> int:
    rikkojat: dict[str, list[str]] = {}
    tiedostot = sorted((juuri / ".devcontainer").glob("*/devcontainer.json"))
    for tiedosto in tiedostot:
        paketti = tiedosto.parent.name
        asetukset = lue_jsonc(tiedosto.read_text("utf-8"))
        for saanto, kunnossa in saannot(juuri, paketti, asetukset).items():
            rikkojat.setdefault(saanto, [])
            if not kunnossa:
                rikkojat[saanto].append(paketti)
    print("kehityskontteja yli 90:", "kyllä" if len(tiedostot) > 90 else "ei")
    for saanto, paketit in rikkojat.items():
        tila = "kyllä" if not paketit else "ei: " + ", ".join(paketit)
        print(f"{saanto}: {tila}")
    return 1 if any(rikkojat.values()) else 0


# @alku tyokalut
ARGUMENTIT = {
    "LISAPAKETIT": "apt-paketit",
    "PIP_PAKETIT": "pip-paketit",
    "NODEJS": "Node.js",
    "NPM_PAKETIT": "npm-paketit",
    "PLAYWRIGHT": "Playwright",
    "KOTLIN": "Kotlin",
    "ANDROID_SDK": "Android SDK",
}


def tyokalut(juuri: Path, paketti: str) -> int:
    """Tulostaa, mitä paketin kehityskontti asentaa peruskuvan lisäksi.
    Samat työkalut tarvitaan, jos esimerkit ajetaan ilman konttia."""
    tiedosto = juuri / ".devcontainer" / paketti / "devcontainer.json"
    if not tiedosto.is_file():
        print(f"paketilla {paketti} ei ole kehityskonttia")
        return 1
    asetukset = lue_jsonc(tiedosto.read_text("utf-8"))
    print(asetukset["name"])
    argumentit = asetukset["build"].get("args", {})
    for nimi, selite in ARGUMENTIT.items():
        if nimi in argumentit:
            print(f"  {selite}: {argumentit[nimi]}")
    if not argumentit:
        print("  peruskuvan työkalut riittävät")
    for valitsin in asetukset.get("runArgs", []):
        print(f"  docker run -valitsin: {valitsin}")
    return 0
# @loppu tyokalut


def main(argumentit: list[str]) -> int:
    juuri = repositorion_juuri()
    if juuri is None:
        print("OHITETTU: tutoriaalien repositoriota ei löydy")
        return 0
    if len(argumentit) == 2 and argumentit[0] == "tyokalut":
        return tyokalut(juuri, argumentit[1])
    if argumentit:
        print(__doc__)
        return 2
    return tarkista_kaikki(juuri)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
