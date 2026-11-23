#!/usr/bin/env python3
"""Tutoriaalien koodiesimerkkien testaaja.

Käyttö:  python3 yhteiset/testaa_esimerkit.py --kieli KIELI <hakemisto>

Kielet: c, cpp, python, bash, rust, go, java, tcl, racket, sql,
systemverilog, vhdl.

Esimerkki on joko yksittäinen lähdetiedosto `esimerkit/<nimi>.<pääte>`
tai hakemisto `esimerkit/<nimi>/`, jonka lähdetiedostot muodostavat yhden
ohjelman. Hakemistoesimerkin pääohjelma on kielen mukaan `main.py`,
`main.sh`, `main.rs`, `main.tcl`, `main.rkt` tai `main.sql`; Javassa
pääluokka on aina `Main`, ja SystemVerilogin ja VHDL:n ylin taso on
`testipenkki`.

Testaaja tekee seuraavat tarkistukset:

1. Jokainen lukujen ja pikaoppaan koodilohko viittaa tiedostoon
   attribuutilla `tiedosto=`, eli käsin kirjoitettua, testaamatonta koodia
   ei ole. Jokainen esimerkkitiedosto on viitattu tekstissä.
2. Esimerkkien rivit ovat enintään 78 merkkiä pitkiä (PDF:n leveys).
3. Esimerkki tarkistetaan ja käännetään kielen työkaluilla varoitukset
   virheinä (esim. GCC/Clang sanitoijineen, ruff ja mypy --strict,
   ShellCheck, Clippy, go vet ja gofmt, javac -Xlint, Verilator -Wall).
4. Ohjelma ajetaan tyhjässä väliaikaisessa työhakemistossa, ja sen
   tulostetta verrataan tiedostoon `<nimi>.odotettu`. Paluuarvon on
   oltava 0. Tiedosto `<nimi>.syote` annetaan syötteeksi ja tiedoston
   `<nimi>.argumentit` rivit komentoriviargumenteiksi.
5. `<nimi>.ei-kaanny.<pääte>` ei saa läpäistä tarkistusta tai käännöstä
   sellaisenaan, mutta sen on läpäistävä korjattuna. C:ssä ja C++:ssa
   korjaus tehdään makrolla -DKORJATTU, muissa kielissä poistamalla
   rivit, joilla on merkintä `@virhe`.
6. `<nimi>.kaatuu.<pääte>` havainnollistaa ajonaikaista virhettä: ajon on
   päätyttävä virheeseen, ja virhetulosteessa on oltava jokainen
   tiedoston `<nimi>.virhe` rivi.
7. C:ssä ja C++:ssa rivi `// TSAN` ajaa esimerkin myös
   ThreadSanitizerilla.

Työkalut voi valita ympäristömuuttujalla ESIMERKIT_KAANTAJAT (C ja C++),
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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

MAKSIMIPITUUS = 78
AIKARAJA_S = 120
SANITOIJAT = ["-g", "-fsanitize=address,undefined",
              "-fno-sanitize-recover=all"]
KOODIKIELET = {
    "c", "cpp", "c++", "python", "bash", "sh", "rust", "go", "java",
    "kotlin", "javascript", "js", "typescript", "ts", "tcl", "racket",
    "scheme", "sql", "verilog", "systemverilog", "vhdl",
}

LOHKO = re.compile(r"^```\s*\{?([^}\n]*)\}?\s*$")
TIEDOSTO_ATTR = re.compile(r'tiedosto="([^"]+)"')


# ---------------------------------------------------------------------
# Kieliprofiilit

@dataclass
class Ajo:
    """Yhden esimerkin yksi testikerta yhdellä toteutuksella."""
    tyokalu: str
    lahteet: list[Path]
    tyohak: Path           # käännöstuotteiden hakemisto
    liput: list[str] = field(default_factory=list)
    korjattu: bool = False


Komennot = Callable[[Ajo], list[list[str]]]


@dataclass(frozen=True)
class Toteutus:
    nimi: str
    tyokalut: tuple[str, ...]      # vaihtoehdot, ensimmäinen löytyvä
    tarkista: Komennot             # tarkistus- ja käännöskomennot
    aja: Callable[[Ajo], list[str]]
    sanitoijat: bool = False       # C/C++: AddressSanitizer + UBSan


@dataclass(frozen=True)
class Kieli:
    paatteet: tuple[str, ...]
    muut: tuple[str, ...]          # esim. otsikkotiedostot
    paaohjelma: str                # hakemistoesimerkin pääohjelma
    toteutukset: tuple[Toteutus, ...]
    korjaus: str = "rivi"          # "makro" (C/C++) tai "rivi"
    stderr_virhe: bool = False     # tyhjästä poikkeava stderr on virhe


def paa(ajo: Ajo, nimi: str) -> Path:
    """Hakemistoesimerkin pääohjelma tai yksittäinen lähdetiedosto."""
    if len(ajo.lahteet) == 1:
        return ajo.lahteet[0]
    for p in ajo.lahteet:
        if p.name == nimi:
            return p
    raise ValueError(f"pääohjelmaa {nimi} ei löydy")


def c_tarkistus(standardi: str, linkitys: list[str]) -> Komennot:
    def komennot(ajo: Ajo) -> list[list[str]]:
        lisa = ["-DKORJATTU"] if ajo.korjattu else []
        return [[ajo.tyokalu, standardi, "-Wall", "-Wextra", "-Wpedantic",
                 "-Werror", *ajo.liput, *lisa, *map(str, ajo.lahteet),
                 "-o", str(ajo.tyohak / "ohjelma"), *linkitys]]
    return komennot


def binaari(ajo: Ajo) -> list[str]:
    return [str(ajo.tyohak / "ohjelma")]


def python_tarkistus(ajo: Ajo) -> list[list[str]]:
    tiedostot = list(map(str, ajo.lahteet))
    return [["ruff", "check", "--no-cache", "--quiet", *tiedostot],
            ["mypy", "--strict", "--no-error-summary",
             f"--cache-dir={ajo.tyohak / 'mypy'}", *tiedostot]]


def go_tarkistus(ajo: Ajo) -> list[list[str]]:
    tiedostot = list(map(str, ajo.lahteet))
    gofmt = str(Path(ajo.tyokalu).with_name("gofmt"))
    return [[sys.executable, "-c",
             "import subprocess,sys; r=subprocess.run(sys.argv[1:],"
             "capture_output=True,text=True); "
             "print(r.stdout+r.stderr, file=sys.stderr); "
             "sys.exit(1 if r.returncode or r.stdout.strip() else 0)",
             gofmt, "-l", *tiedostot],
            [ajo.tyokalu, "vet", *tiedostot],
            [ajo.tyokalu, "build", "-o", str(ajo.tyohak / "ohjelma"),
             *tiedostot]]


def ghdl_tarkistus(ajo: Ajo) -> list[list[str]]:
    return [[ajo.tyokalu, "-a", "--std=08", "--warn-error",
             f"--workdir={ajo.tyohak}", *map(str, ajo.lahteet)],
            [ajo.tyokalu, "-e", "--std=08", f"--workdir={ajo.tyohak}",
             "testipenkki"]]


def ghdl_ajo(ajo: Ajo) -> list[str]:
    # Ubuntun GHDL käyttää mcode-taustaa: simulaatio ajetaan GHDL:llä.
    return [ajo.tyokalu, "-r", "--std=08", f"--workdir={ajo.tyohak}",
            "testipenkki"]


GCC_C = Toteutus("gcc", ("gcc-14", "gcc"), c_tarkistus("-std=c23", ["-lm"]),
                 binaari, sanitoijat=True)
CLANG_C = Toteutus("clang", ("clang-20", "clang"),
                   c_tarkistus("-std=c23", ["-lm"]), binaari,
                   sanitoijat=True)
GCC_CPP = Toteutus("g++", ("g++-14", "g++"), c_tarkistus("-std=c++23", []),
                   binaari, sanitoijat=True)
CLANG_CPP = Toteutus("clang++", ("clang++-20", "clang++"),
                     c_tarkistus("-std=c++23", []), binaari,
                     sanitoijat=True)

KIELET: dict[str, Kieli] = {
    "c": Kieli((".c",), (".h",), "main.c", (GCC_C, CLANG_C), "makro"),
    "cpp": Kieli((".cpp",), (".hpp", ".h"), "main.cpp",
                 (GCC_CPP, CLANG_CPP), "makro"),
    "python": Kieli((".py",), (), "main.py", (Toteutus(
        "python", ("python3",), python_tarkistus,
        lambda a: [a.tyokalu, str(paa(a, "main.py"))]),)),
    "bash": Kieli((".sh",), (), "main.sh", (Toteutus(
        "bash", ("bash",),
        lambda a: [["shellcheck", "-x", *map(str, a.lahteet)]],
        lambda a: [a.tyokalu, str(paa(a, "main.sh"))]),)),
    "rust": Kieli((".rs",), (), "main.rs", (Toteutus(
        "rust", ("/usr/lib/rust-1.80/bin/clippy-driver", "clippy-driver"),
        lambda a: [[a.tyokalu, "--edition", "2021", "-D", "warnings",
                    "-D", "clippy::all", "-C", "debuginfo=1",
                    "--crate-name", "ohjelma",
                    str(paa(a, "main.rs")), "-o",
                    str(a.tyohak / "ohjelma")]],
        binaari),)),
    "go": Kieli((".go",), (), "main.go", (Toteutus(
        "go", ("/usr/lib/go-1.23/bin/go", "go"), go_tarkistus, binaari),)),
    "java": Kieli((".java",), (), "Main.java", (Toteutus(
        "java", ("javac",),
        lambda a: [[a.tyokalu, "-Xlint:all", "-Werror", "-d",
                    str(a.tyohak / "luokat"), *map(str, a.lahteet)]],
        lambda a: ["java", "-cp", str(a.tyohak / "luokat"), "Main"]),)),
    "tcl": Kieli((".tcl",), (), "main.tcl", (Toteutus(
        "tcl", ("tclsh8.6", "tclsh"), lambda a: [],
        lambda a: [a.tyokalu, str(paa(a, "main.tcl"))]),)),
    "racket": Kieli((".rkt",), (), "main.rkt", (Toteutus(
        "racket", ("racket",),
        lambda a: [["raco", "expand", str(paa(a, "main.rkt"))]],
        lambda a: [a.tyokalu, str(paa(a, "main.rkt"))]),),
        stderr_virhe=True),
    "sql": Kieli((".sql",), (), "main.sql", (Toteutus(
        "sqlite", ("sqlite3",), lambda a: [],
        lambda a: [a.tyokalu, "-bail", "-batch", "-init",
                   str(paa(a, "main.sql")), ":memory:", ".quit"]),)),
    "systemverilog": Kieli((".sv",), (".svh",), "testipenkki.sv", (Toteutus(
        "verilator", ("verilator",),
        lambda a: [[a.tyokalu, "--binary", "-Wall", "-Wno-DECLFILENAME",
                    "--top-module", "testipenkki",
                    "-Mdir", str(a.tyohak / "obj"), "-o", "ohjelma",
                    *map(str, a.lahteet)]],
        lambda a: [str(a.tyohak / "obj" / "ohjelma")]),)),
    "vhdl": Kieli((".vhd",), (), "testipenkki.vhd", (Toteutus(
        "ghdl", ("ghdl",), ghdl_tarkistus, ghdl_ajo),)),
}


# ---------------------------------------------------------------------
# Toteutusten etsintä

@dataclass
class Valittu:
    toteutus: Toteutus
    tyokalu: str
    liput: list[str]
    tsan: bool


def toimii(tyokalu: str, liput: list[str], paate: str) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        lahde = Path(tmp) / f"testi{paate}"
        lahde.write_text("int main(void) { return 0; }\n", "utf-8")
        tulos = subprocess.run(
            [tyokalu, *liput, str(lahde), "-o", str(Path(tmp) / "a")],
            capture_output=True)
        return tulos.returncode == 0


def valitse(kieli: Kieli) -> list[Valittu]:
    pyydetyt = os.environ.get("ESIMERKIT_KAANTAJAT", "").split()
    valitut = []
    for t in kieli.toteutukset:
        ehdokkaat = [n for n in t.tyokalut if not pyydetyt or n in pyydetyt]
        tyokalu = next((n for n in ehdokkaat if shutil.which(n)), None)
        if tyokalu is None:
            continue
        liput: list[str] = []
        tsan = False
        if t.sanitoijat:
            if toimii(tyokalu, SANITOIJAT, kieli.paatteet[0]):
                liput = SANITOIJAT
                tsan = toimii(tyokalu, ["-fsanitize=thread"],
                              kieli.paatteet[0])
            else:
                print(f"Huom: {tyokalu} ilman sanitoijia")
        valitut.append(Valittu(t, tyokalu, liput, tsan))
    if not valitut:
        sys.exit("Yhtään työkalua ei löytynyt.")
    return valitut


# ---------------------------------------------------------------------
# Esimerkit

@dataclass
class Esimerkki:
    nimi: str
    lahteet: list[Path]
    tiedostot: list[Path]
    ei_kaanny: bool
    kaatuu: bool
    hakemisto: Path


def etsi_esimerkit(kieli: Kieli, hakemisto: Path) -> list[Esimerkki]:
    esimerkit = []
    for polku in sorted(hakemisto.iterdir()):
        if polku.is_dir():
            lahteet = sorted(p for p in polku.iterdir()
                             if p.suffix in kieli.paatteet)
            tiedostot = sorted(p for p in polku.iterdir()
                               if p.suffix in kieli.paatteet + kieli.muut)
            if lahteet:
                esimerkit.append(Esimerkki(polku.name, lahteet, tiedostot,
                                           False, False, hakemisto))
        elif polku.suffix in kieli.paatteet:
            paate = polku.suffix
            nimi = polku.name.removesuffix(paate)
            ei_kaanny = nimi.endswith(".ei-kaanny")
            kaatuu = nimi.endswith(".kaatuu")
            nimi = nimi.removesuffix(".ei-kaanny").removesuffix(".kaatuu")
            esimerkit.append(Esimerkki(nimi, [polku], [polku], ei_kaanny,
                                       kaatuu, hakemisto))
    return esimerkit


def korjattu_kopio(esimerkki: Esimerkki, kohde: Path) -> list[Path]:
    """Kopioi lähteet ja poistaa rivit, joilla on merkintä @virhe."""
    kohde.mkdir(parents=True, exist_ok=True)
    tulos = []
    for p in esimerkki.lahteet:
        rivit = [r for r in p.read_text("utf-8").splitlines(keepends=True)
                 if "@virhe" not in r]
        uusi = kohde / p.name
        uusi.write_text("".join(rivit), "utf-8")
        tulos.append(uusi)
    return tulos


# ---------------------------------------------------------------------
# Markdown ja rivit

def koodilohkon_kielet(attr: str) -> set[str]:
    sanat = attr.split()
    kielet = {s[1:] for s in sanat if s.startswith(".")}
    if sanat and not sanat[0].startswith((".", "#")) and "=" not in sanat[0]:
        kielet.add(sanat[0])
    return kielet


def tarkista_markdown(juuri: Path) -> tuple[list[str], set[Path]]:
    virheet: list[str] = []
    viitatut: set[Path] = set()
    tiedostot = sorted((juuri / "luvut").glob("*.md"))
    if (juuri / "pikaopas.md").exists():
        tiedostot.append(juuri / "pikaopas.md")
    for md in tiedostot:
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
    """Rivien pituus PDF:n leveyteen. Go-koodin sisennys on gofmt:n
    vaatimuksesta sarkain, ja se lasketaan neljäksi merkiksi."""
    virheet = []
    nimi = tiedosto.relative_to(tiedosto.parent.parent)
    sarkaimet = tiedosto.suffix == ".go"
    for nro, rivi in enumerate(tiedosto.read_text("utf-8").splitlines(), 1):
        pituus = len(rivi.expandtabs(4))
        if pituus > MAKSIMIPITUUS:
            virheet.append(f"{nimi}:{nro}: rivi on liian pitkä "
                           f"({pituus} > {MAKSIMIPITUUS})")
        if "\t" in rivi and not sarkaimet:
            virheet.append(f"{nimi}:{nro}: sarkainmerkki")
    return virheet


# ---------------------------------------------------------------------
# Ajaminen

def ymparisto(tyohak: Path) -> dict[str, str]:
    return dict(os.environ, ASAN_OPTIONS="detect_leaks=1",
                UBSAN_OPTIONS="halt_on_error=1",
                TSAN_OPTIONS="halt_on_error=1",
                GOCACHE=str(tyohak.parent / "go-valimuisti"),
                GOPATH=str(tyohak.parent / "go-polku"),
                GOTOOLCHAIN="local", GO111MODULE="off",
                PYTHONDONTWRITEBYTECODE="1", RUST_BACKTRACE="0")


def suorita(komennot: list[list[str]], env: dict[str, str]
            ) -> tuple[bool, str]:
    for komento in komennot:
        tulos = subprocess.run(komento, capture_output=True, text=True,
                               env=env)
        if tulos.returncode != 0:
            return False, f"$ {' '.join(komento)}\n{tulos.stdout}" \
                          f"{tulos.stderr}"
    return True, ""


def aja(kieli: Kieli, komento: list[str], esimerkki: Esimerkki,
        env: dict[str, str]) -> tuple[bool, str]:
    perus = esimerkki.hakemisto / esimerkki.nimi
    def tiedosto(paate: str) -> Path:
        return perus.with_name(perus.name + paate)
    syote = tiedosto(".syote")
    argumentit = tiedosto(".argumentit")
    with tempfile.TemporaryDirectory() as ajohak:
        try:
            tulos = subprocess.run(
                [*komento, *(argumentit.read_text("utf-8").splitlines()
                             if argumentit.exists() else [])],
                input=syote.read_text("utf-8") if syote.exists() else "",
                capture_output=True, text=True, timeout=AIKARAJA_S,
                env=env, cwd=ajohak)
        except subprocess.TimeoutExpired:
            return False, "aikaraja ylittyi"
    if esimerkki.kaatuu:
        virhe = tiedosto(".virhe")
        if not virhe.exists():
            return False, f"tiedosto {virhe.name} puuttuu"
        if tulos.returncode == 0:
            return False, "ohjelman olisi pitänyt kaatua"
        kaikki = tulos.stdout + tulos.stderr
        for rivi in virhe.read_text("utf-8").splitlines():
            if rivi.strip() and rivi.strip() not in kaikki:
                return False, (f"virhetulosteesta puuttuu '{rivi.strip()}'"
                               f"\n{tulos.stderr}")
        return True, ""
    if tulos.returncode != 0:
        return False, (f"paluuarvo {tulos.returncode}\n"
                       f"{tulos.stdout}\n{tulos.stderr}")
    if kieli.stderr_virhe and tulos.stderr.strip():
        return False, f"virhetuloste ei ole tyhjä:\n{tulos.stderr}"
    odotettu = tiedosto(".odotettu")
    if not odotettu.exists():
        return False, f"tiedosto {odotettu.name} puuttuu"
    if tulos.stdout != odotettu.read_text("utf-8"):
        return False, ("tuloste poikkeaa odotetusta\n--- odotettu\n"
                       f"{odotettu.read_text('utf-8')}\n--- saatu\n"
                       f"{tulos.stdout}")
    return True, ""


def testaa(kieli: Kieli, esimerkki: Esimerkki, valittu: Valittu,
           juuri: Path) -> list[str]:
    t = valittu.toteutus
    tunnus = f"[{t.nimi}] {esimerkki.nimi}"
    tyohak = juuri / f"{esimerkki.nimi}.{t.nimi}"
    tyohak.mkdir(parents=True)
    env = ymparisto(tyohak)
    virheet: list[str] = []

    def ajo(korjattu: bool, liput: list[str], hak: Path) -> Ajo:
        lahteet = esimerkki.lahteet
        if korjattu and kieli.korjaus == "rivi":
            lahteet = korjattu_kopio(esimerkki, hak / "korjattu")
        return Ajo(valittu.tyokalu, lahteet, hak, liput,
                   korjattu and kieli.korjaus == "makro")

    if esimerkki.ei_kaanny:
        ok, _ = suorita(t.tarkista(ajo(False, valittu.liput, tyohak)), env)
        if ok:
            virheet.append(f"{tunnus}: tarkistus tai käännös onnistui, "
                           "vaikka ei pitäisi")
    a = ajo(esimerkki.ei_kaanny, valittu.liput, tyohak)
    ok, viesti = suorita(t.tarkista(a), env)
    if not ok:
        return virheet + [f"{tunnus}: tarkistus tai käännös epäonnistui\n"
                          f"{viesti}"]
    if esimerkki.kaatuu and t.sanitoijat and not valittu.liput:
        return virheet   # ilman sanitoijia kaatumista ei voi todentaa
    ok, viesti = aja(kieli, t.aja(a), esimerkki, env)
    if not ok:
        virheet.append(f"{tunnus}: {viesti}")

    if valittu.tsan and any("// TSAN" in p.read_text("utf-8")
                            for p in esimerkki.tiedostot):
        tsan_hak = tyohak / "tsan"
        tsan_hak.mkdir()
        a = ajo(esimerkki.ei_kaanny, ["-g", "-fsanitize=thread"], tsan_hak)
        ok, viesti = suorita(t.tarkista(a), env)
        if ok:
            ok, viesti = aja(kieli, t.aja(a), esimerkki, env)
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
    valitut = valitse(kieli)
    print("Työkalut:", ", ".join(v.tyokalu for v in valitut))

    virheet, viitatut = tarkista_markdown(juuri)
    for esimerkki in esimerkit:
        for tiedosto in esimerkki.tiedostot:
            virheet += tarkista_rivit(tiedosto)
            if tiedosto.resolve() not in viitatut:
                virheet.append(f"{tiedosto.name}: tiedostoa ei käytetä "
                               "tekstissä")

    with tempfile.TemporaryDirectory() as tmp, \
            concurrent.futures.ThreadPoolExecutor() as pooli:
        tehtavat = [pooli.submit(testaa, kieli, e, v, Path(tmp))
                    for e in esimerkit for v in valitut]
        for tehtava in concurrent.futures.as_completed(tehtavat):
            virheet += tehtava.result()

    ajoja = len(esimerkit) * len(valitut)
    if virheet:
        print("\n\n".join(virheet))
        print(f"\nVIRHEITÄ: {len(virheet)}")
        return 1
    print(f"OK: {len(esimerkit)} esimerkkiä, {ajoja} tarkistusta ja ajoa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
