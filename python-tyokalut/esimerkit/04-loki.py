"""UVM-tyylisen simulaatiolokin jäsentäminen säännöllisellä lausekkeella:
viestit tunnisteittain, ensimmäinen esiintymä ja kuolemaan johtaneet
virheet."""

import re
import sys
from dataclasses import dataclass

# @alku lauseke
VIESTI = re.compile(r"""
    ^(?P<taso>UVM_(?:INFO|WARNING|ERROR|FATAL))\s+
    (?P<tiedosto>\S+)\((?P<rivi>\d+)\)\s+       # tb/scb.sv(142)
    @\s*(?P<aika>\d+)(?P<yksikko>[munp]?s):\s+  # @ 1250ns:
    (?P<polku>\S+)\s+                           # uvm_test_top.env.scb
    \[(?P<tunniste>[^\]]+)\]\s*                 # [VERTAILU]
    (?P<teksti>.*)$
""", re.VERBOSE)
# @loppu lauseke


@dataclass(frozen=True)
class Viesti:
    taso: str
    tunniste: str
    aika_ns: float
    teksti: str


KERROIN_NS = {"s": 1e9, "ms": 1e6, "us": 1e3, "ns": 1.0, "ps": 1e-3}


# @alku jasenna
def jasenna(rivi: str) -> Viesti | None:
    m = VIESTI.match(rivi.rstrip("\n"))
    if m is None:
        return None
    aika = int(m["aika"]) * KERROIN_NS[m["yksikko"]]
    return Viesti(m["taso"].removeprefix("UVM_"), m["tunniste"], aika,
                  m["teksti"])
# @loppu jasenna


def main() -> int:
    ensimmainen: dict[tuple[str, str], Viesti] = {}
    lukumaara: dict[tuple[str, str], int] = {}
    tuntemattomat = 0
    for rivi in sys.stdin:
        viesti = jasenna(rivi)
        if viesti is None:
            tuntemattomat += rivi.strip() != ""
            continue
        avain = (viesti.taso, viesti.tunniste)
        ensimmainen.setdefault(avain, viesti)
        lukumaara[avain] = lukumaara.get(avain, 0) + 1
    for (taso, tunniste), maara in sorted(lukumaara.items()):
        eka = ensimmainen[(taso, tunniste)]
        print(f"{taso:<8}{tunniste:<12}{maara:>3}  "
              f"ensin {eka.aika_ns:g} ns: {eka.teksti}")
    print(f"tunnistamattomia rivejä: {tuntemattomat}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
