"""Aaltomuotojen ohjelmallinen käsittely: simuloidaan laskuri,
jäsennetään VCD ja tarkistetaan laskurin sääntö jokaisella reunalla."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from vuo.vcd import jasenna, naytteet

JUURI = Path(__file__).resolve().parent
LAHTEET = [JUURI / "rtl" / "laskuri.sv", JUURI / "tb" / "laskuri_tb.sv"]


def simuloi(hak: Path) -> Path:
    """Kääntää ja ajaa testipenkin Icaruksella. Palauttaa VCD:n polun."""
    vcd = hak / "laskuri.vcd"
    subprocess.run(["iverilog", "-g2012", "-s", "laskuri_tb", "-o",
                    str(hak / "sim.vvp"), *map(str, LAHTEET)], check=True)
    subprocess.run(["vvp", "-n", str(hak / "sim.vvp"), f"+vcd={vcd}"],
                   check=True, capture_output=True)
    return vcd


# @alku tarkistus
def tarkista(rivit: list[dict[str, int | None]]) -> list[str]:
    """Laskurin sääntö: kun sallittu on 1, arvo kasvaa yhdellä (mod 8)
    ja yli nousee täsmälleen silloin, kun arvo kiertää nollaan."""
    virheet = []
    for i in range(len(rivit) - 1):
        nyt, seur = rivit[i], rivit[i + 1]
        if not nyt["rst_n"] or nyt["arvo"] is None:
            continue
        odotettu = (nyt["arvo"] + 1) % 8 if nyt["sallittu"] else nyt["arvo"]
        if seur["arvo"] != odotettu:
            virheet.append(f"reuna {i}: arvo {seur['arvo']}, "
                           f"odotettu {odotettu}")
        if nyt["sallittu"] and seur["yli"] != int(nyt["arvo"] == 7):
            virheet.append(f"reuna {i}: yli {seur['yli']}")
    return virheet
# @loppu tarkistus


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        signaalit = jasenna(simuloi(Path(tmp)))
    lyhyet = ["rst_n", "sallittu", "arvo", "yli"]
    rivit = [{n: r[f"laskuri_tb.{n}"] for n in lyhyet}
             for r in naytteet(signaalit, "laskuri_tb.clk",
                               [f"laskuri_tb.{n}" for n in lyhyet])]
    print("signaaleja:", len(signaalit), " reunoja:", len(rivit))
    print("reuna rst_n sallittu arvo yli")
    for i, r in enumerate(rivit):
        print(f"{i:5}", *(f"{'x' if r[n] is None else r[n]:>{len(n)}}"
                          for n in lyhyet))
    virheet = tarkista(rivit)
    print("laskurin sääntö:", virheet or "OK")

    # Sama tarkistus löytää vian: arvo, joka ei kasva.
    rikki = [dict(r) for r in rivit]
    rikki[6]["arvo"] = rikki[5]["arvo"]
    print("muutettu näyte:", tarkista(rikki))
    return 1 if virheet else 0


if __name__ == "__main__":
    sys.exit(main())
