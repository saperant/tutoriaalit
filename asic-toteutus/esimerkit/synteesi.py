"""Yosys-synteesi Pythonista: RTL → standardisoluista koottu netlista.

Synteesi ajetaan väliaikaisessa hakemistossa. Tulos sisältää Yosysin
JSON-netlistan (jota ajoitusanalyysi käyttää), Verilog-netlistan ja
solujen määrät.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HAK = Path(__file__).parent
KIRJASTO = HAK / "opetus.lib"


@dataclass
class Tulos:
    json: dict[str, Any]
    verilog: str
    top: str

    def moduuli(self) -> dict[str, Any]:
        m: dict[str, Any] = self.json["modules"][self.top]
        return m

    def solut(self) -> Counter[str]:
        return Counter(c["type"] for c in self.moduuli()["cells"].values())


# @alku syntetisoi
def syntetisoi(lahteet: list[Path], top: str, abc: str = "",
               litista: bool = True) -> Tulos:
    """Syntetisoi RTL:n opetuskirjaston soluiksi Yosysilla."""
    with tempfile.TemporaryDirectory() as tmp:
        luku = "; ".join(f"read_verilog -sv {p}" for p in lahteet)
        skripti = (
            f"{luku}; "
            f"synth -top {top}{' -flatten' if litista else ''}; "
            f"dfflibmap -liberty {KIRJASTO}; "         # kiikut
            f"abc -liberty {KIRJASTO} {abc}; "         # logiikka
            "opt_clean -purge; "
            f"write_json {tmp}/n.json; "
            f"write_verilog -noattr {tmp}/n.v")
        subprocess.run(["yosys", "-q", "-p", skripti], check=True,
                       capture_output=True, text=True)
        data = json.loads(Path(tmp, "n.json").read_text("utf-8"))
        verilog = Path(tmp, "n.v").read_text("utf-8")
    return Tulos(data, verilog, top)
# @loppu syntetisoi


def rakenteellinen(nimi: str, m: dict[str, Any]) -> str:
    """Kirjoittaa JSON-netlistan rakenteelliseksi Verilogiksi."""
    nimet: dict[int, str] = {}
    for portti, p in m["ports"].items():
        for i, b in enumerate(p["bits"]):
            nimet.setdefault(b, f"{portti}[{i}]" if len(p["bits"]) > 1
                             else portti)

    def johdin(b: int | str) -> str:
        if isinstance(b, str):
            return f"1'b{b}"
        return nimet.get(b, f"n{b}")

    rivit = [f"module {nimi} ("]
    portit = []
    for portti, p in m["ports"].items():
        leveys = f" [{len(p['bits']) - 1}:0]" if len(p["bits"]) > 1 else ""
        portit.append(f"  {p['direction']} wire{leveys} {portti}")
    rivit.append(",\n".join(portit) + "\n);")
    sisaiset = sorted({b for c in m["cells"].values()
                       for v in c["connections"].values() for b in v
                       if isinstance(b, int) and b not in nimet})
    rivit += [f"  wire n{b};" for b in sisaiset]
    for i, c in enumerate(m["cells"].values()):
        yhteydet = ", ".join(f".{p}({johdin(v[0])})"
                             for p, v in c["connections"].items())
        rivit.append(f"  {c['type']} s{i} ({yhteydet});")
    # Lähtöportti, joka on sama johdin kuin toinen portti (esim. scan_out
    # ja q[7]), kytketään erikseen.
    for portti, p in m["ports"].items():
        b = p["bits"][0]
        if p["direction"] == "output" and nimet[b] != portti \
                and len(p["bits"]) == 1:
            rivit.append(f"  assign {portti} = {nimet[b]};")
    return "\n".join(rivit + ["endmodule", ""])


def pinta_ala(tulos: Tulos, alat: dict[str, float]) -> float:
    return sum(alat[t] * n for t, n in tulos.solut().items())


def solujen_alat() -> dict[str, float]:
    teksti = KIRJASTO.read_text("utf-8")
    return {m[1]: float(m[2]) for m in re.finditer(
        r"cell \((\w+)\) \{\s*area : ([\d.]+);", teksti)}


def main() -> None:
    # @alku kaytto
    tulos = syntetisoi([HAK / "laskuri.v"], "laskuri")
    alat = solujen_alat()
    for solu, maara in sorted(tulos.solut().items()):
        print(f"{solu:10} {maara:3}  {alat[solu] * maara:7.2f} µm²")
    print(f"yhteensä   {sum(tulos.solut().values()):3}  "
          f"{pinta_ala(tulos, alat):7.2f} µm²")
    # @loppu kaytto


if __name__ == "__main__":
    main()
