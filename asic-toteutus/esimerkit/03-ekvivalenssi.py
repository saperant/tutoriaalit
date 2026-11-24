"""Onko netlista sama piiri kuin RTL? Simulointi ja muodollinen todistus.

1. Sama testipenkki ajetaan Icarus Verilogilla RTL:lle ja synteesin
   tuottamalle porttitason netlistalle, ja tulosteita verrataan.
2. Yosys todistaa kombinatorisen kertojan netlistan ekvivalentiksi
   RTL:n kanssa kaikilla syötteillä (miter + SAT), ja löytää
   vastaesimerkin, kun netlistaan tehdään virhe.
3. Puutteellinen herkkyyslista saa RTL-simuloinnin ja synteesin
   tuloksen eroamaan: virhe näkyy vasta porttitason simuloinnissa.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

from synteesi import syntetisoi

HAK = Path(__file__).parent
SOLUT = HAK / "opetus_solut.v"


# @alku simuloi
def simuloi(tiedostot: list[Path]) -> list[str]:
    """Kääntää ja ajaa Icarus Verilogilla; palauttaa tulosterivit."""
    with tempfile.TemporaryDirectory() as tmp:
        ohjelma = Path(tmp, "sim")
        subprocess.run(["iverilog", "-g2012", "-o", str(ohjelma),
                        *map(str, tiedostot)], check=True)
        ajo = subprocess.run(["vvp", "-n", str(ohjelma)], check=True,
                             capture_output=True, text=True)
    return [r for r in ajo.stdout.splitlines()
            if r and "$finish" not in r]


def netlista_tiedostoon(verilog: str, hak: Path) -> Path:
    polku = hak / "netlista.v"
    polku.write_text(verilog, "utf-8")
    return polku
# @loppu simuloi


# @alku miter
def todista(kultainen: Path, netlista: Path) -> str:
    """Miter-piiri: molemmat toteutukset rinnakkain, lähdöt XOR:ataan.
    SAT-ratkaisija etsii syötteen, jolla jokin lähtöbitti eroaa."""
    skripti = (
        f"read_verilog {kultainen}; prep -top kerto6; "
        "rename kerto6 kultainen; design -stash kultainen; "
        f"read_verilog {netlista} {SOLUT}; "
        "hierarchy -top kerto6; flatten; proc; opt_clean; "
        "rename kerto6 portti; design -stash portti; "
        "design -copy-from kultainen -as kultainen kultainen; "
        "design -copy-from portti -as portti portti; "
        "miter -equiv -flatten -make_outputs kultainen portti miter; "
        "hierarchy -top miter; "
        "sat -prove trigger 0 -show-inputs miter")
    ajo = subprocess.run(["yosys", "-p", skripti], check=True,
                         capture_output=True, text=True)
    if "no model found: SUCCESS" in ajo.stdout:
        return "ekvivalentti kaikilla 4096 syötteellä"
    a = re.search(r"\\in_a\s+(\d+)", ajo.stdout)
    b = re.search(r"\\in_b\s+(\d+)", ajo.stdout)
    assert a and b
    return f"eroaa, vastaesimerkki a={a[1]} b={b[1]}"
# @loppu miter


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        hak = Path(tmp)
        # @alku simulointi
        tulos = syntetisoi([HAK / "kertoja.v"], "kertoja")
        netlista = netlista_tiedostoon(tulos.verilog, hak)
        tp = HAK / "tp_kertoja.v"
        rtl = simuloi([HAK / "kertoja.v", tp])
        portit = simuloi([netlista, SOLUT, tp])
        print(f"simulointi: {len(rtl)} tulosta, "
              f"{'samat' if rtl == portit else 'EROAVAT'}")
        # @loppu simulointi

        # @alku todistus
        kombi = syntetisoi([HAK / "kerto6.v"], "kerto6")
        netlista = netlista_tiedostoon(kombi.verilog, hak)
        print("muodollinen:", todista(HAK / "kerto6.v", netlista))
        # Virhe: vaihdetaan netlistan ensimmäinen XOR XNOR:ksi.
        rikki = kombi.verilog.replace("XOR2_X1 ", "XNOR2_X1 ", 1)
        netlista = netlista_tiedostoon(rikki, hak)
        print("muodollinen, rikottu netlista:",
              todista(HAK / "kerto6.v", netlista))
        # @loppu todistus

        # @alku epasuhta-ajo
        tp = HAK / "tp_epasuhta.v"
        print("RTL-simulointi:   ",
              " | ".join(simuloi([HAK / "epasuhta.v", tp])))
        tulos = syntetisoi([HAK / "epasuhta.v"], "epasuhta")
        netlista = netlista_tiedostoon(tulos.verilog, hak)
        print("porttisimulointi: ",
              " | ".join(simuloi([netlista, SOLUT, tp])))
        # @loppu epasuhta-ajo


if __name__ == "__main__":
    main()
