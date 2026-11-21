#!/usr/bin/env python3
"""Tutoriaalien C- ja C++-esimerkkien testaaja.

Käyttö:  python3 yhteiset/testaa_esimerkit.py [--kieli c|cpp] <hakemisto>

Esimerkki on joko yksittäinen lähdetiedosto `esimerkit/<nimi>.cpp`
(C:ssä `.c`) tai hakemisto `esimerkit/<nimi>/`, jonka kaikki
lähdetiedostot käännetään yhdeksi ohjelmaksi.

Testaaja tekee seuraavat tarkistukset:

1. Jokainen Markdownin C- tai C++-koodilohko viittaa tiedostoon
   attribuutilla `tiedosto=`, eli käsin kirjoitettua, testaamatonta
   koodia ei ole.
2. Jokainen viitattu tiedosto on olemassa ja jokainen esimerkkitiedosto
   on viitattu tekstissä.
3. Esimerkkien rivit ovat enintään 78 merkkiä pitkiä (PDF:n leveys).
4. Jokainen esimerkki käännetään jokaisella löytyvällä kääntäjällä
   varoitukset virheinä sekä AddressSanitizerin ja
   UndefinedBehaviorSanitizerin kanssa.
5. Ohjelma ajetaan tyhjässä väliaikaisessa työhakemistossa, ja sen
   tulostetta verrataan tiedostoon `<nimi>.odotettu`. Paluuarvon on
   oltava 0. Tiedosto `<nimi>.syote` annetaan ohjelman syötteeksi ja
   tiedoston `<nimi>.argumentit` rivit komentoriviargumenteiksi.
6. Tiedostot `<nimi>.ei-kaanny.cpp` (tai `.c`) eivät saa kääntyä
   sellaisenaan, mutta niiden on käännyttävä makrolla -DKORJATTU.
   Näin varmistetaan, että virhe johtuu juuri esitellystä kohdasta.
7. Jos lähdekoodissa on rivi `// TSAN`, esimerkki käännetään ja ajetaan
   myös ThreadSanitizerilla.
8. Tiedostot `<nimi>.kaatuu.cpp` (tai `.c`) havainnollistavat virheitä,
   jotka sanitoijat havaitsevat ajon aikana. Niiden on käännyttävä,
   mutta ajon on päätyttävä virheeseen, ja virhetulosteessa on oltava
   jokainen tiedoston `<nimi>.virhe` rivi. Tuloste ennen kaatumista
   verrataan tiedostoon `<nimi>.odotettu` kuten muissakin esimerkeissä.

Kääntäjät voi valita ympäristömuuttujalla ESIMERKIT_KAANTAJAT,
esim. ESIMERKIT_KAANTAJAT="g++-14 clang++".
"""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

VAROITUKSET = ["-Wall", "-Wextra", "-Wpedantic", "-Werror"]
SANITOIJAT = ["-g", "-fsanitize=address,undefined",
              "-fno-sanitize-recover=all"]
MAKSIMIPITUUS = 78
AIKARAJA_S = 60
KOODIKIELET = {"c", "cpp", "c++"}

LOHKO = re.compile(r"^```\s*\{?([^}\n]*)\}?\s*$")
TIEDOSTO_ATTR = re.compile(r'tiedosto="([^"]+)"')


@dataclass(frozen=True)
class Kieli:
    paate: str
    otsikot: tuple[str, ...]
    standardi: str
    # Oletuksena käytetään ensimmäistä löytyvää kääntäjää kustakin
    # ryhmästä.
    kaantajat: tuple[tuple[str, ...], ...]
    linkitys: tuple[str, ...]


KIELET = {
    "cpp": Kieli(".cpp", (".hpp", ".h"), "-std=c++23",
                 (("g++-14", "g++"), ("clang++-20", "clang++")), ()),
    "c": Kieli(".c", (".h",), "-std=c23",
               (("gcc-14", "gcc"), ("clang-20", "clang")), ("-lm",)),
}


@dataclass
class Kaantaja:
    nimi: str
    liput: list[str]
    tsan: bool


@dataclass
class Esimerkki:
    nimi: str               # esim. "01-hei"
    lahteet: list[Path]     # käännettävät tiedostot
    tiedostot: list[Path]   # kaikki tiedostot otsikot mukaan lukien
    ei_kaanny: bool
    hakemisto: Path         # esimerkit-hakemisto
    kaatuu: bool = False         # esimerkit-hakemisto


def sanitoijat_toimivat(kieli: Kieli, kaantaja: str,
                        liput: list[str]) -> bool:
    """Tarkistaa, että sanitoijien ajonaikaiset kirjastot löytyvät."""
    with tempfile.TemporaryDirectory() as tmp:
        lahde = Path(tmp) / f"testi{kieli.paate}"
        lahde.write_text("int main(void) { return 0; }\n", "utf-8")
        tulos = subprocess.run(
            [kaantaja, *liput, str(lahde), "-o", str(Path(tmp) / "a")],
            capture_output=True)
        return tulos.returncode == 0


def etsi_kaantajat(kieli: Kieli) -> list[Kaantaja]:
    pyydetyt = os.environ.get("ESIMERKIT_KAANTAJAT")
    if pyydetyt:
        ehdokkaat = []
        for nimi in pyydetyt.split():
            if shutil.which(nimi) is None:
                sys.exit(f"Kääntäjää ei löydy: {nimi}")
            ehdokkaat.append(nimi)
    else:
        ehdokkaat = [next(n for n in ryhma if shutil.which(n))
                     for ryhma in kieli.kaantajat
                     if any(shutil.which(n) for n in ryhma)]
    if not ehdokkaat:
        sys.exit("Yhtään kääntäjää ei löytynyt.")

    loydetyt = []
    for nimi in ehdokkaat:
        if sanitoijat_toimivat(kieli, nimi, SANITOIJAT):
            tsan = sanitoijat_toimivat(kieli, nimi, ["-fsanitize=thread"])
            loydetyt.append(Kaantaja(nimi, SANITOIJAT, tsan))
        else:
            print(f"Huom: {nimi} ilman sanitoijia (kirjastot puuttuvat)")
            loydetyt.append(Kaantaja(nimi, [], tsan=False))
    return loydetyt


def etsi_esimerkit(kieli: Kieli, hakemisto: Path) -> list[Esimerkki]:
    esimerkit = []
    for polku in sorted(hakemisto.iterdir()):
        if polku.is_dir():
            lahteet = sorted(polku.glob(f"*{kieli.paate}"))
            tiedostot = sorted(
                p for p in polku.iterdir()
                if p.suffix in (kieli.paate, *kieli.otsikot))
            if lahteet:
                esimerkit.append(Esimerkki(polku.name, lahteet, tiedostot,
                                           False, hakemisto))
        elif polku.suffix == kieli.paate:
            ei_kaanny = polku.name.endswith(".ei-kaanny" + kieli.paate)
            kaatuu = polku.name.endswith(".kaatuu" + kieli.paate)
            nimi = polku.name.removesuffix(kieli.paate)
            nimi = nimi.removesuffix(".ei-kaanny").removesuffix(".kaatuu")
            esimerkit.append(Esimerkki(nimi, [polku], [polku], ei_kaanny,
                                       hakemisto, kaatuu))
    return esimerkit


def koodilohkon_kielet(attr: str) -> set[str]:
    sanat = attr.split()
    kielet = {s[1:] for s in sanat if s.startswith(".")}
    if sanat and not sanat[0].startswith((".", "#")) and "=" not in sanat[0]:
        kielet.add(sanat[0])
    return kielet


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
            elif koodilohkon_kielet(attr) & KOODIKIELET:
                virheet.append(f"{paikka}: koodilohko ilman tiedostoa")
    return virheet, viitatut


def tarkista_rivit(tiedosto: Path) -> list[str]:
    virheet = []
    nimi = tiedosto.relative_to(tiedosto.parent.parent)
    for nro, rivi in enumerate(tiedosto.read_text("utf-8").splitlines(), 1):
        if len(rivi) > MAKSIMIPITUUS:
            virheet.append(f"{nimi}:{nro}: rivi on liian pitkä "
                           f"({len(rivi)} > {MAKSIMIPITUUS})")
        if "\t" in rivi:
            virheet.append(f"{nimi}:{nro}: sarkainmerkki")
    return virheet


def kaanna(kieli: Kieli, kaantaja: str, liput: list[str],
           esimerkki: Esimerkki, kohde: Path,
           lisa: list[str] | None = None):
    komento = [kaantaja, kieli.standardi, *VAROITUKSET, *liput,
               *(lisa or []), *map(str, esimerkki.lahteet),
               "-o", str(kohde), *kieli.linkitys]
    return subprocess.run(komento, capture_output=True, text=True)


def aja(ohjelma: Path, esimerkki: Esimerkki) -> tuple[bool, str]:
    perus = esimerkki.hakemisto / esimerkki.nimi
    odotettu_polku = perus.with_name(perus.name + ".odotettu")
    syote_polku = perus.with_name(perus.name + ".syote")
    argumentit_polku = perus.with_name(perus.name + ".argumentit")
    syote = syote_polku.read_text("utf-8") if syote_polku.exists() else ""
    argumentit = (argumentit_polku.read_text("utf-8").splitlines()
                  if argumentit_polku.exists() else [])
    env = dict(os.environ, ASAN_OPTIONS="detect_leaks=1",
               UBSAN_OPTIONS="halt_on_error=1",
               TSAN_OPTIONS="halt_on_error=1")
    with tempfile.TemporaryDirectory() as tyohak:
        try:
            tulos = subprocess.run([str(ohjelma), *argumentit],
                                   input=syote, capture_output=True,
                                   text=True, timeout=AIKARAJA_S, env=env,
                                   cwd=tyohak)
        except subprocess.TimeoutExpired:
            return False, "aikaraja ylittyi"
    if esimerkki.kaatuu:
        virhe_polku = perus.with_name(perus.name + ".virhe")
        if not virhe_polku.exists():
            return False, f"tiedosto {virhe_polku.name} puuttuu"
        if tulos.returncode == 0:
            return False, "ohjelman olisi pitänyt kaatua"
        for rivi in virhe_polku.read_text("utf-8").splitlines():
            if rivi.strip() and rivi.strip() not in tulos.stderr:
                return False, (f"virhetulosteesta puuttuu '{rivi.strip()}'"
                               f"\n{tulos.stderr}")
    elif tulos.returncode != 0:
        return False, (f"paluuarvo {tulos.returncode}\n"
                       f"{tulos.stdout}\n{tulos.stderr}")
    if not odotettu_polku.exists():
        return False, f"tiedosto {odotettu_polku.name} puuttuu"
    odotettu = odotettu_polku.read_text("utf-8")
    if tulos.stdout != odotettu:
        return False, ("tuloste poikkeaa odotetusta\n--- odotettu\n"
                       f"{odotettu}\n--- saatu\n{tulos.stdout}")
    return True, ""


def testaa(kieli: Kieli, esimerkki: Esimerkki, kaantaja: Kaantaja,
           tyohak: Path) -> list[str]:
    virheet = []
    tunnus = f"[{kaantaja.nimi}] {esimerkki.nimi}"
    kohde = tyohak / f"{esimerkki.nimi}.{kaantaja.nimi}"
    lisa = ["-DKORJATTU"] if esimerkki.ei_kaanny else []

    if esimerkki.ei_kaanny:
        tulos = kaanna(kieli, kaantaja.nimi, kaantaja.liput, esimerkki,
                       kohde)
        if tulos.returncode == 0:
            virheet.append(f"{tunnus}: käännös onnistui, vaikka ei pitäisi")
    tulos = kaanna(kieli, kaantaja.nimi, kaantaja.liput, esimerkki, kohde,
                   lisa)
    if tulos.returncode != 0:
        virheet.append(f"{tunnus}: käännös epäonnistui\n{tulos.stderr}")
        return virheet

    if esimerkki.kaatuu and not kaantaja.liput:
        return virheet   # ilman sanitoijia kaatumista ei voi todentaa
    ok, viesti = aja(kohde, esimerkki)
    if not ok:
        virheet.append(f"{tunnus}: {viesti}")

    tsan_merkinta = any("// TSAN" in p.read_text("utf-8")
                        for p in esimerkki.tiedostot)
    if kaantaja.tsan and tsan_merkinta:
        tsan_kohde = kohde.with_suffix(".tsan")
        tulos = kaanna(kieli, kaantaja.nimi, ["-g", "-fsanitize=thread"],
                       esimerkki, tsan_kohde, lisa)
        if tulos.returncode != 0:
            virheet.append(f"{tunnus} (TSan): käännös epäonnistui\n"
                           f"{tulos.stderr}")
        else:
            ok, viesti = aja(tsan_kohde, esimerkki)
            if not ok:
                virheet.append(f"{tunnus} (TSan): {viesti}")
    return virheet


def main() -> int:
    jasennin = argparse.ArgumentParser(
        description="Testaa tutoriaalin koodiesimerkit.")
    jasennin.add_argument("--kieli", choices=sorted(KIELET), default="cpp")
    jasennin.add_argument("hakemisto", type=Path)
    argumentit = jasennin.parse_args()

    kieli = KIELET[argumentit.kieli]
    juuri = argumentit.hakemisto.resolve()
    esimerkit = etsi_esimerkit(kieli, juuri / "esimerkit")
    kaantajat = etsi_kaantajat(kieli)
    print("Kääntäjät:", ", ".join(k.nimi for k in kaantajat))

    virheet, viitatut = tarkista_markdown(juuri)
    for esimerkki in esimerkit:
        for tiedosto in esimerkki.tiedostot:
            virheet += tarkista_rivit(tiedosto)
            if tiedosto.resolve() not in viitatut:
                virheet.append(f"{tiedosto.name}: tiedostoa ei käytetä "
                               "tekstissä")

    with tempfile.TemporaryDirectory() as tmp, \
            concurrent.futures.ThreadPoolExecutor() as pooli:
        tehtavat = [pooli.submit(testaa, kieli, e, k, Path(tmp))
                    for e in esimerkit for k in kaantajat]
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
