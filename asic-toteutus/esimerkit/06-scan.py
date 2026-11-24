"""Scan-ketjun lisääminen netlistaan ja sen testaus simuloimalla.

Jokainen kiikku vaihdetaan scan-kiikuksi (SDFF_X1), jonka SE-tulo
valitsee datan: SE=0 toiminnallinen D, SE=1 edellisen kiikun lähtö.
Testeri siirtää tilan sisään, ajaa yhden toiminnallisen jakson ja
siirtää tuloksen ulos. Juuttumisvika näkyy väärinä bitteinä.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Any

from synteesi import rakenteellinen, syntetisoi

HAK = Path(__file__).parent


# @alku ketju
def lisaa_scan(m: dict[str, Any]) -> int:
    """Vaihtaa kiikut scan-kiikuiksi ja ketjuttaa ne q[0]:sta alkaen.
    Lisää portit scan_en, scan_in ja scan_out. Palauttaa pituuden."""
    bitit = [b for n in m["netnames"].values() for b in n["bits"]
             if isinstance(b, int)]
    uusi = max(bitit) + 1
    se, si = uusi, uusi + 1
    m["ports"]["scan_en"] = {"direction": "input", "bits": [se]}
    m["ports"]["scan_in"] = {"direction": "input", "bits": [si]}
    q = m["ports"]["q"]["bits"]
    kiikut = sorted((c for c in m["cells"].values()
                     if c["type"] == "DFF_X1"),
                    key=lambda c: q.index(c["connections"]["Q"][0]))
    edellinen = si
    for c in kiikut:
        c["type"] = "SDFF_X1"
        c["connections"]["SE"] = [se]
        c["connections"]["SI"] = [edellinen]
        edellinen = c["connections"]["Q"][0]
    m["ports"]["scan_out"] = {"direction": "output", "bits": [edellinen]}
    return len(kiikut)
# @loppu ketju


def aja(netlista: str) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        polku = Path(tmp, "n.v")
        polku.write_text(netlista, "utf-8")
        sim = Path(tmp, "sim")
        subprocess.run(["iverilog", "-o", str(sim), str(polku),
                        str(HAK / "opetus_solut.v"),
                        str(HAK / "tp_scan.v")], check=True)
        tulos = subprocess.run(["vvp", "-n", str(sim)], check=True,
                               capture_output=True, text=True)
    return [r for r in tulos.stdout.splitlines() if "$finish" not in r]


def main() -> None:
    # @alku ajo
    tulos = syntetisoi([HAK / "laskuri.v"], "laskuri")
    m = tulos.moduuli()
    print(f"scan-ketjussa {lisaa_scan(m)} kiikkua")
    print("ehjä piiri:  ", " | ".join(aja(rakenteellinen("laskuri", m))))
    # Juuttumisvika: ensimmäisen NAND-portin lähtö pysyvästi 1:ssä.
    nand = next(c for c in m["cells"].values() if c["type"] == "NAND2_X1")
    nand["connections"]["A"] = ["0"]
    print("vika (SA1):  ", " | ".join(aja(rakenteellinen("laskuri", m))))
    # @loppu ajo


if __name__ == "__main__":
    main()
