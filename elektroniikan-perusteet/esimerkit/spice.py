"""Apufunktiot ngspicen ajamiseen Pythonista.

Esimerkit kutsuvat ngspiceä eräajona (`ngspice -b`), lukevat sen
tulostamat mittaukset (`meas`, `print`) ja `wrdata`-komennolla
kirjoitetut datatiedostot ja vertaavat niitä käsin laskettuihin arvoihin.
Ajettuna suoraan moduuli tarkistaa, että ngspice toimii.
"""

from __future__ import annotations

import math
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import numpy.typing as npt

HAKEMISTO = Path(__file__).resolve().parent

# Rivit muotoa "nimi = 1.234560e-03" (meas ja print).
ARVO = re.compile(r"^\s*([@A-Za-z_][\w().#@\[\]]*)\s*=\s*([-+0-9.eE]+)")


@dataclass
class Tulos:
    """Simulaation tulokset: nimetyt arvot (viimeisin ja kaikki, jos
    sama nimi toistuu silmukassa) ja wrdata-tiedostojen sarakkeet."""

    arvot: dict[str, float] = field(default_factory=dict)
    sarjat: dict[str, list[float]] = field(default_factory=dict)
    data: dict[str, npt.NDArray[np.float64]] = field(default_factory=dict)
    tuloste: str = ""


# @alku simuloi
def simuloi(lahde: str) -> Tulos:
    """Ajaa piirin ngspicellä eräajona väliaikaisessa hakemistossa.

    `lahde` on .cir-tiedoston nimi esimerkkihakemistossa tai netlist
    tekstinä. Mallikirjastot (*.lib) kopioidaan mukaan. Piirin
    .control-lohko ajaa analyysit; `meas`- ja `print`-tulokset ja
    `wrdata`-tiedostot palautetaan.
    """
    cir = lahde.endswith(".cir")
    teksti = (HAKEMISTO / lahde).read_text("utf-8") if cir else lahde
    with tempfile.TemporaryDirectory() as hak:
        piiri = Path(hak) / "piiri.cir"
        piiri.write_text(teksti, "utf-8")
        for malli in HAKEMISTO.glob("*.lib"):     # .include-mallikirjastot
            (Path(hak) / malli.name).write_text(malli.read_text("utf-8"))
        ajo = subprocess.run(["ngspice", "-b", "piiri.cir"], cwd=hak,
                             capture_output=True, text=True, timeout=60,
                             check=False)
        tuloste = ajo.stdout + ajo.stderr
        if ajo.returncode != 0 or "Error" in tuloste:
            raise RuntimeError(f"ngspice epäonnistui:\n{tuloste}")
        tulos = Tulos(tuloste=tuloste)
        for rivi in tuloste.splitlines():
            osuma = ARVO.match(rivi)
            if osuma:
                nimi, arvo = osuma.group(1).lower(), float(osuma.group(2))
                tulos.arvot[nimi] = arvo
                tulos.sarjat.setdefault(nimi, []).append(arvo)
        for dat in Path(hak).glob("*.dat"):
            tulos.data[dat.stem] = np.loadtxt(dat, ndmin=2)
    return tulos
# @loppu simuloi


# @alku muotoile
ETULIITTEET = [(1e-12, "p"), (1e-9, "n"), (1e-6, "u"), (1e-3, "m"),
               (1.0, ""), (1e3, "k"), (1e6, "M")]


def muotoile(arvo: float, yksikko: str) -> str:
    """Arvo kolmella merkitsevällä numerolla ja SI-etuliitteellä."""
    if arvo == 0:
        return f"0 {yksikko}"
    kerroin, etuliite = ETULIITTEET[0]
    for k, e in ETULIITTEET:
        if abs(arvo) >= k * 0.9995:
            kerroin, etuliite = k, e
    luku = float(f"{arvo / kerroin:.3g}")   # pyöristys ennen muotoilua
    numerot = max(0, 2 - int(math.floor(math.log10(abs(luku)))))
    return f"{luku:.{numerot}f} {etuliite}{yksikko}"
# @loppu muotoile


# @alku vertaa
VIRHEET: list[str] = []


def vertaa(nimi: str, simuloitu: float, laskettu: float, yksikko: str,
           sallittu: float = 0.01) -> None:
    """Tulostaa simuloidun ja lasketun arvon ja tarkistaa suhteellisen
    eron. Liian suuri ero kirjataan, ja `lopeta` palauttaa virhekoodin."""
    mittakaava = max(abs(laskettu), 1e-15)
    ero = abs(simuloitu - laskettu) / mittakaava
    tila = "ok" if ero <= sallittu else "EROAA"
    print(f"  {nimi:<12} simuloitu {muotoile(simuloitu, yksikko):>10}"
          f"   laskettu {muotoile(laskettu, yksikko):>10}   {tila}")
    if tila != "ok":
        VIRHEET.append(nimi)


def lopeta() -> None:
    """Päättää ohjelman virhekoodilla, jos jokin vertailu epäonnistui."""
    if VIRHEET:
        print("eroavat:", ", ".join(VIRHEET), file=sys.stderr)
        sys.exit(1)
# @loppu vertaa


if __name__ == "__main__":
    # Itsetesti: jännitteenjako 10 V, 1 kohm ja 1 kohm.
    tulos = simuloi("""itsetesti
V1 a 0 10
R1 a b 1k
R2 b 0 1k
.control
op
print v(b)
.endc
.end
""")
    print("ngspice toimii")
    vertaa("v(b)", tulos.arvot["v(b)"], 5.0, "V")
    for arvo in (4.7e3, 0.0147, 1.5e-9, 220.0, 2.2e6, 0.999e-3):
        print(f"  {arvo:g} -> {muotoile(arvo, 'X')}")
    lopeta()
