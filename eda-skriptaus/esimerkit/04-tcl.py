"""Tcl työkalun sisällä: Yosysin Tcl-tila ja opetus-sta eräajona."""

from __future__ import annotations

import tempfile
from pathlib import Path

from vuo.ajo import aja
from vuo.kulku import tclsh
from vuo.raportit import lue_ltp, lue_sta, lue_yosys_stat

JUURI = Path(__file__).resolve().parent
TCL = JUURI / "tcl"
LEVEYDET = [4, 8, 16]


# @alku yosys
def synteesi(tmp: Path) -> None:
    ajo = aja(["yosys", "-q", "-c", str(TCL / "synteesi.tcl")],
              tmp / "synteesi.log",
              ymparisto={"LEVEYDET": " ".join(map(str, LEVEYDET)),
                         "RTL": str(JUURI / "rtl" / "laskuri.sv"),
                         "TULOS": str(tmp)})
    print(f"yosys -c synteesi.tcl: paluuarvo {ajo.paluuarvo}")
    solut, syvyydet = [], []
    for w in LEVEYDET:
        res = lue_yosys_stat(tmp / f"stat_{w}.json")
        solut.append(res.solut)
        syvyydet.append(lue_ltp((tmp / f"ltp_{w}.txt").read_text()))
        print(f"  LEVEYS={w:2}: kiikkuja {res.kiikut:2} "
              f"(LEVEYS + 1: {'kyllä' if res.kiikut == w + 1 else 'EI'})")
    print(f"  solumäärä kasvaa leveyden mukana: "
          f"{'kyllä' if solut == sorted(set(solut)) else 'EI'}")
    print(f"  pisin polku ei lyhene: "
          f"{'kyllä' if syvyydet == sorted(syvyydet) else 'EI'}")
# @loppu yosys


# @alku sta
def sta(tmp: Path, skripti: str, leveys: int, jakso: float) -> None:
    ajo = aja([tclsh(), str(TCL / "opetus_sta.tcl"), "-source",
               str(TCL / skripti), "--", str(tmp / f"laskuri_{leveys}.blif"),
               str(jakso), str(tmp / "sta.txt")], tmp / "sta.log")
    if ajo.onnistui:
        ajoitus = lue_sta((tmp / "sta.txt").read_text())
        tila = "MET" if ajoitus.kunnossa else "VIOLATED"
        print(f"  {skripti}, LEVEYS={leveys}, {jakso} ns: {tila}")
    else:
        virhe = [r for r in ajo.loki.read_text().splitlines()
                 if r.startswith("Error:")]
        print(f"  {skripti}: paluuarvo {ajo.paluuarvo}")
        print(f"  {virhe[0]}")
# @loppu sta


def sieto(tmp: Path) -> None:
    rtl = JUURI / "rtl" / "laskuri.sv"
    ajo = aja(["yosys", "-q", "-c", str(TCL / "sieto.tcl")],
              tmp / "sieto.log",
              ymparisto={"RTL_UUSI": str(tmp / "laskuri_v2.sv"),
                         "RTL": str(rtl)})
    tulosteet = [r for r in ajo.loki.read_text().splitlines()
                 if not r.startswith(("$", "ERROR"))]
    print(f"yosys -c sieto.tcl: paluuarvo {ajo.paluuarvo}")
    for rivi in tulosteet:
        print(f"  {rivi}")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        hak = Path(tmp)
        synteesi(hak)
        print("opetus-sta:")
        for w in LEVEYDET:
            sta(hak, "sta_kulku.tcl", w, 10.0)
        sta(hak, "sta_kulku.tcl", 4, 0.5)
        sta(hak, "sta_rikki.tcl", 4, 10.0)
        sieto(hak)


if __name__ == "__main__":
    main()
