#!/usr/bin/env python3
"""Tiivistää Yosysin ja nextpnr:n raportit tarkistettaviksi riveiksi.

Käyttö:
  raportti.py NIMI STAT.json PNR.json [--solut-alle N] [--solut-yli N]
              [--fmax-yli MHZ] [--fmax-alle MHZ] [--vain-ajoitus]

Tulostaa solutyyppien määrät synteesin jälkeen sekä logiikkasolujen
määrän ja jokaisen kellon suurimman taajuuden sijoittelun ja reitityksen
jälkeen. Logiikkasolujen määrä ja Fmax vaihtelevat työkaluversioittain,
joten ne tulostetaan raja-arvoihin verrattuina; tarkat luvut ovat
raporttitiedostoissa.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

# Solutyypit, joiden määrä tulostetaan sellaisenaan.
NIMET = {
    "SB_CARRY": "kantoketjun soluja (SB_CARRY)",
    "SB_RAM40_4K": "lohko-RAM (SB_RAM40_4K)",
    "SB_MAC16": "DSP-lohkoja (SB_MAC16)",
    "SB_PLL40_PAD": "PLL (SB_PLL40_PAD)",
}


def kellon_nimi(nextpnr_nimi: str) -> str:
    """'clk$SB_IO_IN_$glb_clk' -> 'clk'."""
    return nextpnr_nimi.split("$")[0]


def main() -> int:
    j = argparse.ArgumentParser(description=__doc__)
    j.add_argument("nimi")
    j.add_argument("stat", type=Path)
    j.add_argument("pnr", type=Path)
    j.add_argument("--solut-alle", type=int)
    j.add_argument("--solut-yli", type=int)
    j.add_argument("--fmax-yli", action="append", default=[])
    j.add_argument("--fmax-alle", type=float)
    j.add_argument(
        "--vain-ajoitus",
        action="store_true",
        help="ei solutyyppejä, vain logiikkasolut ja Fmax",
    )
    a = j.parse_args()

    stat = json.loads(a.stat.read_text("utf-8"))["design"]
    solut: dict[str, int] = stat["num_cells_by_type"]
    pnr = json.loads(a.pnr.read_text("utf-8"))

    print(f"== {a.nimi}")
    for tyyppi, selite in NIMET.items():
        if tyyppi in solut and not a.vain_ajoitus:
            print(f"{selite}: {solut[tyyppi]}")

    lc = pnr["utilization"]["ICESTORM_LC"]["used"]
    if a.solut_alle is not None:
        tulos = "kyllä" if lc < a.solut_alle else f"EI ({lc})"
        print(f"logiikkasoluja alle {a.solut_alle}: {tulos}")
    if a.solut_yli is not None:
        tulos = "kyllä" if lc > a.solut_yli else f"EI ({lc})"
        print(f"logiikkasoluja yli {a.solut_yli}: {tulos}")

    # nextpnr voi raportoida myös sisäisiä verkkoja ($-alkuiset nimet).
    fmax = {
        kellon_nimi(k): v["achieved"]
        for k, v in pnr["fmax"].items()
        if not k.startswith("$")
    }
    for raja in a.fmax_yli:
        kello, _, mhz = raja.rpartition("=")
        kellot = [kello] if kello else sorted(fmax)
        for k in kellot:
            if k not in fmax:
                print(f"Fmax {k}: ei ajoituspolkuja")
                continue
            tulos = "kyllä" if fmax[k] > float(mhz) else f"EI ({fmax[k]:.1f})"
            print(f"Fmax {k} yli {mhz} MHz: {tulos}")
    if a.fmax_alle is not None:
        for k in sorted(fmax):
            tulos = (
                "kyllä" if fmax[k] < a.fmax_alle else f"EI ({fmax[k]:.1f})"
            )
            print(f"Fmax {k} alle {a.fmax_alle:g} MHz: {tulos}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
