"""Regressioajon tuloshakemiston läpikäynti pathlibillä.

Hakemistorakenne luodaan ensin tilapäishakemistoon, jotta esimerkki on
itsenäinen. Oikeassa työkalussa juuri annettaisiin argumenttina.
"""

import sys
import tempfile
from pathlib import Path

# @alku rakenne
TIEDOSTOT = {
    "uart_perus/siemen_1/sim.log": "TESTI LÄPI\n",
    "uart_perus/siemen_2/sim.log": "TESTI LÄPI\n",
    "uart_perus/siemen_2/aaltomuoto.vcd": "$date ... $end\n",
    "uart_virheet/siemen_7/sim.log": "UVM_ERROR ...\nTESTI EPÄONNISTUI\n",
    "fifo_taysi/siemen_1/kesken.tmp": "",
}


def luo(juuri: Path) -> None:
    for nimi, sisalto in TIEDOSTOT.items():
        polku = juuri / nimi
        polku.parent.mkdir(parents=True, exist_ok=True)
        polku.write_text(sisalto, encoding="utf-8")
# @loppu rakenne


# @alku lapikaynti
def tulokset(juuri: Path) -> dict[str, str]:
    """testi/siemen -> 'läpi' | 'epäonnistui' | 'ei lokia'."""
    tulos = {}
    # sorted: tiedostojärjestelmän järjestys ei ole määritelty.
    for ajo in sorted(p for p in juuri.glob("*/siemen_*") if p.is_dir()):
        avain = ajo.relative_to(juuri).as_posix()
        loki = ajo / "sim.log"
        if not loki.is_file():
            tulos[avain] = "ei lokia"
        elif "TESTI LÄPI" in loki.read_text(encoding="utf-8"):
            tulos[avain] = "läpi"
        else:
            tulos[avain] = "epäonnistui"
    return tulos
# @loppu lapikaynti


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        juuri = Path(tmp)
        luo(juuri)
        for avain, tila in tulokset(juuri).items():
            print(f"{avain:<24}{tila}")
        # @alku haku
        vcd = sorted(p.relative_to(juuri) for p in juuri.rglob("*.vcd"))
        koko = sum(p.stat().st_size for p in juuri.rglob("*")
                   if p.is_file())
        print("aaltomuodot:", [p.as_posix() for p in vcd])
        print(f"yhteensä {koko} tavua")
        print("pääte:", (juuri / "uart_perus/siemen_1/sim.log").suffix,
              "| nimi ilman päätettä:",
              (juuri / "a/b/kesken.tmp").stem)
        # @loppu haku
    return 0


if __name__ == "__main__":
    sys.exit(main())
