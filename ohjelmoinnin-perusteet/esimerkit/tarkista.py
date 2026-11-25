"""Tarkistaa lukujen "Kokeile itse" -tehtävien ratkaisut.

Käyttö hakemistossa esimerkit:
  python3 tarkista.py --lista           luettelee tehtävät
  python3 tarkista.py --aloita 03-1     kopioi pohjan: tehtavat/omat/03-1.py
  python3 tarkista.py 03-1              tarkistaa oman ratkaisun
  python3 tarkista.py 03-1 polku.py     tarkistaa annetun tiedoston
"""

import argparse
import ast
import contextlib
import io
import math
import runpy
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any

TEHTAVAT = Path(__file__).resolve().parent / "tehtavat"
POHJAT = TEHTAVAT / "pohjat"
RATKAISUT = TEHTAVAT / "ratkaisut"
TUKI = TEHTAVAT / "tuki"
OMAT = TEHTAVAT / "omat"
AIKARAJA_S = 10


# @alku sama
def sama(saatu: object, odotettu: object) -> bool:
    """Kertoo, vastaako ratkaisun tulos odotettua arvoa."""
    if isinstance(odotettu, bool) or isinstance(saatu, bool):
        return saatu is odotettu            # True ei kelpaa luvuksi 1
    if isinstance(odotettu, float):         # liukuluvuille pieni toleranssi
        return (isinstance(saatu, (int, float))
                and math.isclose(saatu, odotettu, abs_tol=1e-9))
    if isinstance(odotettu, (list, tuple)):
        return (type(saatu) is type(odotettu)
                and len(saatu) == len(odotettu)
                and all(sama(saatu[i], odotettu[i])
                        for i in range(len(odotettu))))
    return type(saatu) is type(odotettu) and saatu == odotettu
# @loppu sama


def lue_tehtavat() -> dict[str, dict[str, Any]]:
    with open(TEHTAVAT / "tehtavat.toml", "rb") as tiedosto:
        return tomllib.load(tiedosto)


def viimeinen_rivi(virhe: BaseException) -> str:
    return f"{type(virhe).__name__}: {virhe}"


def aja_ohjelma(polku: Path, tapaus: dict[str, Any]) -> str | None:
    """Ajaa ohjelman syötteellä. Palauttaa virheen kuvauksen tai None."""
    syote = "".join(rivi + "\n" for rivi in tapaus["syote"])
    odotettu = [rivi.rstrip() for rivi in tapaus["tuloste"]]
    try:
        ajo = subprocess.run(
            [sys.executable, str(polku)], input=syote, text=True,
            capture_output=True, timeout=AIKARAJA_S, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return f"  ohjelma ei päättynyt {AIKARAJA_S} sekunnissa"
    saatu = [rivi.rstrip() for rivi in ajo.stdout.rstrip().splitlines()]
    if ajo.returncode == 0 and saatu == odotettu:
        return None
    rivit = ["  syöte:    " + " | ".join(tapaus["syote"]),
             "  odotettu: " + " | ".join(odotettu),
             "  saatu:    " + " | ".join(saatu)]
    if ajo.returncode != 0:
        virherivit = ajo.stderr.strip().splitlines() or ["(ei viestiä)"]
        rivit.append("  ohjelma kaatui: " + virherivit[-1])
    return "\n".join(rivit)


def lataa(polku: Path) -> tuple[dict[str, Any], str]:
    """Suorittaa tiedoston ja palauttaa sen nimet ja tulosteen."""
    tuloste = io.StringIO()
    vanha_syote = sys.stdin
    sys.stdin = io.StringIO("")
    try:
        with contextlib.redirect_stdout(tuloste):
            nimet = runpy.run_path(str(polku), run_name="tehtava")
    finally:
        sys.stdin = vanha_syote
    return nimet, tuloste.getvalue()


def aja_kutsu(nimet: dict[str, Any], tapaus: dict[str, Any]) -> str | None:
    """Arvioi kutsun ratkaisun nimillä. Palauttaa virheen tai None."""
    ymparisto = dict(nimet)
    rivit = ["  kutsu:    " + tapaus["kutsu"]]
    if "alustus" in tapaus:
        rivit.insert(0, "  alustus:  " + tapaus["alustus"])
    saatu: object
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(tapaus.get("alustus", ""), ymparisto)
            saatu = eval(tapaus["kutsu"], ymparisto)
    except Exception as virhe:  # noqa: BLE001 - ratkaisun mikä tahansa virhe
        luokat = [luokka.__name__ for luokka in type(virhe).__mro__]
        if tapaus.get("virhe") in luokat:
            return None
        saatu = "poikkeus " + viimeinen_rivi(virhe)
    else:
        if "virhe" not in tapaus and sama(
                saatu, ast.literal_eval(tapaus["tulos"])):
            return None
        saatu = repr(saatu)
    if "virhe" in tapaus:
        rivit.append("  odotettu: poikkeus " + tapaus["virhe"])
    else:
        rivit.append("  odotettu: " + tapaus["tulos"])
    rivit.append(f"  saatu:    {saatu}")
    return "\n".join(rivit)


def aja_pytest(testit: Path, toteutus: Path, moduli: str) -> bool:
    """Ajaa testitiedoston annettua toteutusta vasten."""
    with tempfile.TemporaryDirectory() as hakemisto:
        shutil.copy(testit, Path(hakemisto) / "test_tehtava.py")
        shutil.copy(toteutus, Path(hakemisto) / f"{moduli}.py")
        ajo = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
            cwd=hakemisto, capture_output=True, text=True,
            timeout=6 * AIKARAJA_S)
    return ajo.returncode == 0


def tarkista_testit(polku: Path, tehtava: dict[str, Any]) -> str | None:
    """Tehtävä, jossa kirjoitetaan testejä: testien pitää hyväksyä
    oikea toteutus ja hylätä jokainen virheellinen."""
    moduli = tehtava["moduli"]
    if not aja_pytest(polku, TUKI / f"{moduli}.py", moduli):
        return (f"  testisi eivät mene läpi oikealla toteutuksella "
                f"({moduli}.py)\n  aja itse: python3 -m pytest {polku}")
    for virheellinen in sorted((TUKI / tehtava["virheelliset"]).glob("*.py")):
        if aja_pytest(polku, virheellinen, moduli):
            kuvaus = (ast.get_docstring(ast.parse(
                virheellinen.read_text("utf-8"))) or "").splitlines()[0]
            return ("  testisi eivät huomaa virheellistä toteutusta:\n"
                    f"  {kuvaus}")
    return None


def tarkista(tunnus: str, tehtava: dict[str, Any], polku: Path) -> bool:
    """Tarkistaa yhden ratkaisun ja tulostaa tuloksen."""
    otsikko = f"{tunnus} {tehtava['otsikko']}"
    if not polku.exists():
        print(f"{otsikko}: tiedostoa {polku} ei ole.")
        print(f"  Aloita komennolla: python3 tarkista.py --aloita {tunnus}")
        return False
    if "moduli" in tehtava:
        virhe = tarkista_testit(polku, tehtava)
        if virhe:
            print(f"{otsikko}: ei mene läpi.\n{virhe}")
        else:
            print(f"{otsikko}: testit hyväksyvät oikean toteutuksen ja "
                  "hylkäävät virheelliset.")
        return virhe is None

    tapaukset = tehtava["tapaus"]
    nimet: dict[str, Any] = {}
    if any("kutsu" in tapaus for tapaus in tapaukset):
        try:
            nimet, tuloste = lataa(polku)
        except BaseException as poikkeus:  # noqa: BLE001 - myös SystemExit
            print(f"{otsikko}: tiedoston suoritus epäonnistui.\n"
                  f"  {viimeinen_rivi(poikkeus)}")
            if isinstance(poikkeus, EOFError):
                print("  Tiedosto lukee syötettä jo ladattaessa. Tarkistin "
                      "kutsuu funktioita\n  suoraan: pääohjelma ei saa "
                      "käynnistyä, kun tiedosto tuodaan.")
            return False
        if tehtava.get("hiljainen_tuonti") and tuloste:
            print(f"{otsikko}: tiedosto tulostaa jotakin, kun se tuodaan "
                  "modulina.\n  Siirrä pääohjelma funktioon main ja ehdon "
                  'if __name__ == "__main__": taakse.')
            return False
        rekursio = tehtava.get("rekursiivinen")
        if rekursio and rekursio in nimet and (
                rekursio not in nimet[rekursio].__code__.co_names):
            print(f"{otsikko}: funktio {rekursio} ei kutsu itseään.")
            return False
    for nro, tapaus in enumerate(tapaukset, start=1):
        if "kutsu" in tapaus:
            virhe = aja_kutsu(nimet, tapaus)
        else:
            virhe = aja_ohjelma(polku, tapaus)
        if virhe:
            print(f"{otsikko}: tapaus {nro}/{len(tapaukset)} ei mene "
                  f"läpi.\n{virhe}")
            return False
    print(f"{otsikko}: {len(tapaukset)}/{len(tapaukset)} tapausta oikein.")
    return True


def aloita(tunnus: str, tehtava: dict[str, Any]) -> int:
    """Kopioi tehtäväpohjan omien ratkaisujen hakemistoon."""
    OMAT.mkdir(exist_ok=True)
    kohde = OMAT / f"{tunnus}.py"
    if kohde.exists():
        print(f"{kohde} on jo olemassa; sitä ei korvata.")
        return 1
    shutil.copy(POHJAT / f"{tunnus}.py", kohde)
    print(f"Pohja kopioitu: {kohde}")
    if "moduli" in tehtava:
        moduli = f"{tehtava['moduli']}.py"
        shutil.copy(TUKI / moduli, OMAT / moduli)
        print(f"Testattava moduli: {OMAT / moduli}")
    return 0


def tarkista_kaikki(hakemisto: Path, odotus: bool) -> int:
    """Ylläpitäjän tarkistus: malliratkaisujen pitää mennä läpi
    (odotus True) ja pohjien jäädä kiinni (odotus False)."""
    vaarin = []
    tehtavat = lue_tehtavat()
    for tunnus, tehtava in tehtavat.items():
        with contextlib.redirect_stdout(io.StringIO()):
            tulos = tarkista(tunnus, tehtava, hakemisto / f"{tunnus}.py")
        if tulos != odotus:
            vaarin.append(tunnus)
    if vaarin:
        print(f"{hakemisto.name}: väärä tulos tehtävissä "
              + ", ".join(vaarin))
        return 1
    return 0


def main() -> int:
    jasennin = argparse.ArgumentParser(
        description="Tarkistaa Kokeile itse -tehtävien ratkaisut.")
    jasennin.add_argument("tehtava", nargs="?", help="tunnus, esim. 03-1")
    jasennin.add_argument("tiedosto", nargs="?", type=Path,
                          help="oletus: tehtavat/omat/TUNNUS.py")
    jasennin.add_argument("--lista", action="store_true")
    jasennin.add_argument("--aloita", metavar="TUNNUS")
    jasennin.add_argument("--ratkaisut", action="store_true",
                          help="aja malliratkaisut (make testaa)")
    jasennin.add_argument("--pohjat", action="store_true",
                          help="varmista, ettei pohja läpäise tarkistusta")
    valinnat = jasennin.parse_args()
    tehtavat = lue_tehtavat()

    if valinnat.ratkaisut:
        return tarkista_kaikki(RATKAISUT, odotus=True)
    if valinnat.pohjat:
        return tarkista_kaikki(POHJAT, odotus=False)
    if valinnat.lista:
        for tunnus, tehtava in tehtavat.items():
            tila = "  (aloitettu)" if (OMAT / f"{tunnus}.py").exists() else ""
            print(f"{tunnus}  {tehtava['otsikko']}{tila}")
        return 0
    tunnus = valinnat.aloita or valinnat.tehtava
    if tunnus is None:
        luvut = sorted({nimi[:2] for nimi in tehtavat})
        print(f"Tehtäviä on {len(tehtavat)}, "
              f"luvuissa {luvut[0]}–{luvut[-1]}.")
        print("Luettelo:  python3 tarkista.py --lista")
        print("Aloitus:   python3 tarkista.py --aloita 02-1")
        print("Tarkistus: python3 tarkista.py 02-1")
        return 0
    if tunnus not in tehtavat:
        print(f"Tehtävää {tunnus} ei ole. Luettelo: --lista")
        return 1
    if valinnat.aloita:
        return aloita(tunnus, tehtavat[tunnus])
    polku = valinnat.tiedosto or OMAT / f"{tunnus}.py"
    return 0 if tarkista(tunnus, tehtavat[tunnus], polku) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nKeskeytetty. Jäikö ratkaisu ikuiseen silmukkaan?")
        sys.exit(1)
