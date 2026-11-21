#!/usr/bin/env python3
"""Tutoriaalin C++-esimerkkien testaaja.

Käyttö:  python3 yhteiset/testaa_esimerkit.py <tutoriaalin hakemisto>

Testaaja tekee seuraavat tarkistukset:

1. Jokainen Markdownin ```cpp-lohko viittaa tiedostoon attribuutilla
   `tiedosto=`, eli käsin kirjoitettua, testaamatonta koodia ei ole.
2. Jokainen viitattu tiedosto on olemassa ja jokainen esimerkki on
   viitattu tekstissä.
3. Esimerkkien rivit ovat enintään 78 merkkiä pitkiä (PDF:n leveys).
4. Jokainen esimerkki käännetään jokaisella löytyvällä kääntäjällä
   varoitukset virheinä. GCC:llä käytetään lisäksi AddressSanitizeria
   ja UndefinedBehaviorSanitizeria.
5. Ohjelma ajetaan ja sen tulostetta verrataan tiedostoon
   `<nimi>.odotettu`. Paluuarvon on oltava 0.
6. Tiedostot, joiden nimi päättyy `.ei-kaanny.cpp`, eivät saa kääntyä
   sellaisenaan, mutta niiden on käännyttävä makrolla -DKORJATTU.
   Näin varmistetaan, että virhe johtuu juuri esitellystä kohdasta.
7. Jos tiedostossa on rivi `// TSAN`, se käännetään ja ajetaan myös
   ThreadSanitizerilla.

Kääntäjät voi valita ympäristömuuttujalla ESIMERKIT_KAANTAJAT,
esim. ESIMERKIT_KAANTAJAT="g++-14 clang++".
"""

from __future__ import annotations

import concurrent.futures
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

STANDARDI = "-std=c++23"
VAROITUKSET = ["-Wall", "-Wextra", "-Wpedantic", "-Werror"]
MAKSIMIPITUUS = 78
AIKARAJA_S = 60

LOHKO = re.compile(r"^```\s*\{?([^}\n]*)\}?\s*$")
TIEDOSTO_ATTR = re.compile(r'tiedosto="([^"]+)"')


@dataclass
class Kaantaja:
    nimi: str
    liput: list[str]
    tsan: bool


def sanitoijat_toimivat(kaantaja: str, liput: list[str]) -> bool:
    """Tarkistaa, että sanitoijien ajonaikaiset kirjastot löytyvät."""
    with tempfile.TemporaryDirectory() as tmp:
        lahde = Path(tmp) / "testi.cpp"
        lahde.write_text("int main() { return 0; }\n", "utf-8")
        tulos = subprocess.run(
            [kaantaja, *liput, str(lahde), "-o", str(Path(tmp) / "a")],
            capture_output=True)
        return tulos.returncode == 0


# Oletuksena käytetään ensimmäistä löytyvää kääntäjää kustakin ryhmästä.
OLETUSKAANTAJAT = [["g++-14", "g++"], ["clang++-20", "clang++"]]
SANITOIJAT = ["-g", "-fsanitize=address,undefined",
              "-fno-sanitize-recover=all"]


def etsi_kaantajat() -> list[Kaantaja]:
    pyydetyt = os.environ.get("ESIMERKIT_KAANTAJAT")
    if pyydetyt:
        ehdokkaat = []
        for nimi in pyydetyt.split():
            if shutil.which(nimi) is None:
                sys.exit(f"Kääntäjää ei löydy: {nimi}")
            ehdokkaat.append(nimi)
    else:
        ehdokkaat = [next(n for n in ryhma if shutil.which(n))
                     for ryhma in OLETUSKAANTAJAT
                     if any(shutil.which(n) for n in ryhma)]
    if not ehdokkaat:
        sys.exit("Yhtään C++-kääntäjää ei löytynyt.")

    loydetyt = []
    for nimi in ehdokkaat:
        if sanitoijat_toimivat(nimi, SANITOIJAT):
            tsan = sanitoijat_toimivat(nimi, ["-fsanitize=thread"])
            loydetyt.append(Kaantaja(nimi, SANITOIJAT, tsan))
        else:
            print(f"Huom: {nimi} ilman sanitoijia (kirjastot puuttuvat)")
            loydetyt.append(Kaantaja(nimi, [], tsan=False))
    return loydetyt


def tarkista_markdown(juuri: Path) -> tuple[list[str], set[Path]]:
    virheet: list[str] = []
    viitatut: set[Path] = set()
    for md in sorted((juuri / "luvut").glob("*.md")):
        koodissa = False
        for nro, rivi in enumerate(md.read_text("utf-8").splitlines(), 1):
            osuma = LOHKO.match(rivi.strip())
            if not osuma:
                continue
            if koodissa:
                koodissa = False
                continue
            koodissa = True
            attr = osuma.group(1)
            tiedosto = TIEDOSTO_ATTR.search(attr)
            paikka = f"{md.relative_to(juuri)}:{nro}"
            if tiedosto:
                polku = juuri / tiedosto.group(1)
                if not polku.exists():
                    virheet.append(f"{paikka}: tiedostoa ei ole: {polku}")
                viitatut.add(polku.resolve())
            elif re.search(r"\bc(pp|\+\+)\b", attr):
                virheet.append(f"{paikka}: cpp-lohko ilman tiedostoa")
    return virheet, viitatut


def tarkista_rivit(tiedosto: Path) -> list[str]:
    virheet = []
    for nro, rivi in enumerate(tiedosto.read_text("utf-8").splitlines(), 1):
        if len(rivi) > MAKSIMIPITUUS:
            virheet.append(f"{tiedosto.name}:{nro}: rivi on liian pitkä "
                           f"({len(rivi)} > {MAKSIMIPITUUS})")
        if "\t" in rivi:
            virheet.append(f"{tiedosto.name}:{nro}: sarkainmerkki")
    return virheet


def kaanna(kaantaja: str, liput: list[str], lahde: Path,
           kohde: Path, lisa: list[str] | None = None):
    komento = [kaantaja, STANDARDI, *VAROITUKSET, *liput, *(lisa or []),
               str(lahde), "-o", str(kohde)]
    return subprocess.run(komento, capture_output=True, text=True)


def aja(ohjelma: Path, lahde: Path) -> tuple[bool, str]:
    odotettu_polku = lahde.with_name(
        lahde.name.removesuffix(".cpp").removesuffix(".ei-kaanny")
        + ".odotettu")
    syote_polku = odotettu_polku.with_suffix(".syote")
    syote = syote_polku.read_text("utf-8") if syote_polku.exists() else ""
    env = dict(os.environ, ASAN_OPTIONS="detect_leaks=1",
               UBSAN_OPTIONS="halt_on_error=1",
               TSAN_OPTIONS="halt_on_error=1")
    try:
        tulos = subprocess.run([str(ohjelma)], input=syote,
                               capture_output=True, text=True,
                               timeout=AIKARAJA_S, env=env,
                               cwd=lahde.parent)
    except subprocess.TimeoutExpired:
        return False, "aikaraja ylittyi"
    if tulos.returncode != 0:
        return False, (f"paluuarvo {tulos.returncode}\n"
                       f"{tulos.stdout}\n{tulos.stderr}")
    if not odotettu_polku.exists():
        return False, f"tiedosto {odotettu_polku.name} puuttuu"
    odotettu = odotettu_polku.read_text("utf-8")
    if tulos.stdout != odotettu:
        return False, ("tuloste poikkeaa odotetusta\n--- odotettu\n"
                       f"{odotettu}\n--- saatu\n{tulos.stdout}")
    return True, ""


def testaa(lahde: Path, kaantaja: Kaantaja, tyohak: Path) -> list[str]:
    virheet = []
    tunnus = f"[{kaantaja.nimi}] {lahde.name}"
    kohde = tyohak / f"{lahde.stem}.{kaantaja.nimi}"
    ei_kaanny = lahde.name.endswith(".ei-kaanny.cpp")

    if ei_kaanny:
        tulos = kaanna(kaantaja.nimi, kaantaja.liput, lahde, kohde)
        if tulos.returncode == 0:
            virheet.append(f"{tunnus}: käännös onnistui, vaikka ei pitäisi")
        tulos = kaanna(kaantaja.nimi, kaantaja.liput, lahde, kohde,
                       ["-DKORJATTU"])
    else:
        tulos = kaanna(kaantaja.nimi, kaantaja.liput, lahde, kohde)
    if tulos.returncode != 0:
        virheet.append(f"{tunnus}: käännös epäonnistui\n{tulos.stderr}")
        return virheet

    ok, viesti = aja(kohde, lahde)
    if not ok:
        virheet.append(f"{tunnus}: {viesti}")

    if kaantaja.tsan and "// TSAN" in lahde.read_text("utf-8"):
        tsan_kohde = kohde.with_suffix(".tsan")
        lisa = ["-DKORJATTU"] if ei_kaanny else []
        tulos = kaanna(kaantaja.nimi, ["-g", "-fsanitize=thread"], lahde,
                       tsan_kohde, lisa)
        if tulos.returncode != 0:
            virheet.append(f"{tunnus} (TSan): käännös epäonnistui\n"
                           f"{tulos.stderr}")
        else:
            ok, viesti = aja(tsan_kohde, lahde)
            if not ok:
                virheet.append(f"{tunnus} (TSan): {viesti}")
    return virheet


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    juuri = Path(sys.argv[1]).resolve()
    esimerkit = sorted((juuri / "esimerkit").glob("*.cpp"))
    kaantajat = etsi_kaantajat()
    print("Kääntäjät:", ", ".join(k.nimi for k in kaantajat))

    virheet, viitatut = tarkista_markdown(juuri)
    for lahde in esimerkit:
        virheet += tarkista_rivit(lahde)
        if lahde.resolve() not in viitatut:
            virheet.append(f"{lahde.name}: esimerkkiä ei käytetä tekstissä")

    with tempfile.TemporaryDirectory() as tmp, \
            concurrent.futures.ThreadPoolExecutor() as pooli:
        tehtavat = {
            pooli.submit(testaa, lahde, k, Path(tmp)): (lahde, k)
            for lahde in esimerkit for k in kaantajat
        }
        for tehtava in concurrent.futures.as_completed(tehtavat):
            virheet += tehtava.result()

    testeja = len(esimerkit) * len(kaantajat)
    if virheet:
        print("\n\n".join(virheet))
        print(f"\nVIRHEITÄ: {len(virheet)}")
        return 1
    print(f"OK: {len(esimerkit)} esimerkkiä, {testeja} käännöstä ja ajoa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
