#!/usr/bin/env python3
"""Ajaa yhden esimerkkihakemiston ja vertaa tulosta tallennettuun.

Käyttö:  python3 aja.py [--kirjoita] [--ei-tyyppeja] HAKEMISTO

1. mypy --strict tarkistaa hakemiston Python-tiedostot (paitsi
   valitsimella --ei-tyyppeja: TDD:n ensimmäisessä punaisessa vaiheessa
   testattavaa moduulia ei vielä ole).
2. Jos hakemistossa on main.py, se ajetaan. Muuten ajetaan pytest, ja
   liitännäinen tulostin.py kirjoittaa tulokset vakiomuodossa.
3. Tulosta verrataan tiedostoon HAKEMISTO/odotettu. Epäonnistuva testi
   ei ole virhe, jos se on odotettu: osa esimerkeistä näyttää
   nimenomaan, minkä vian testi löytää.

--kirjoita tallentaa tuloksen odotetuksi (tarkista muutos silmin).
"""

from __future__ import annotations

import difflib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TAMA = Path(__file__).resolve().parent


def tyypit(hakemisto: Path, tmp: Path) -> bool:
    tulos = subprocess.run(
        ["mypy", "--strict", "--python-version", "3.12",
         "--no-error-summary", f"--cache-dir={tmp / 'mypy'}", "."],
        cwd=hakemisto, capture_output=True, text=True, check=False)
    if tulos.returncode != 0:
        print(f"{hakemisto.name}: mypy\n{tulos.stdout}{tulos.stderr}")
    return tulos.returncode == 0


def tuloste(hakemisto: Path, tmp: Path) -> str:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=str(TAMA),
               HYPOTHESIS_STORAGE_DIRECTORY=str(tmp / "hypothesis"),
               TULOSTIN_TIEDOSTO=str(tmp / "tulos.txt"))
    if (hakemisto / "main.py").exists():
        ajo = subprocess.run([sys.executable, "main.py"], cwd=hakemisto,
                             env=env, capture_output=True, text=True,
                             timeout=300, check=False)
        if ajo.returncode != 0:
            return f"paluuarvo {ajo.returncode}\n{ajo.stdout}{ajo.stderr}"
        return ajo.stdout
    ajo = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         "-p", "tulostin", "."],
        cwd=hakemisto, env=env, capture_output=True, text=True,
        timeout=300, check=False)
    tulos = tmp / "tulos.txt"
    if not tulos.exists():
        return f"pytest ei käynnistynyt\n{ajo.stdout}{ajo.stderr}"
    return tulos.read_text("utf-8")


def main() -> int:
    argumentit = sys.argv[1:]
    kirjoita = "--kirjoita" in argumentit
    ei_tyyppeja = "--ei-tyyppeja" in argumentit
    polut = [a for a in argumentit if not a.startswith("--")]
    if len(polut) != 1:
        print(__doc__)
        return 2
    hakemisto = Path(polut[0]).resolve()
    nimi = hakemisto.relative_to(TAMA)
    with tempfile.TemporaryDirectory() as tmp_nimi:
        tmp = Path(tmp_nimi)
        if not ei_tyyppeja and not tyypit(hakemisto, tmp):
            return 1
        saatu = tuloste(hakemisto, tmp)
    odotettu = hakemisto / "odotettu"
    if kirjoita:
        odotettu.write_text(saatu, "utf-8")
        print(f"{nimi}: odotettu kirjoitettu")
        return 0
    vanha = odotettu.read_text("utf-8") if odotettu.exists() else ""
    if saatu != vanha:
        print(f"VIRHE: {nimi}: tulos poikkeaa odotetusta")
        sys.stdout.writelines(difflib.unified_diff(
            vanha.splitlines(keepends=True),
            saatu.splitlines(keepends=True), "odotettu", "saatu"))
        return 1
    print(f"OK: {nimi}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
