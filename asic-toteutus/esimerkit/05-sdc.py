"""SDC-rajoitteet: kello, tulojen ja lähtöjen viiveet, monisyklipolku.

Jäsennin (sdc.py) lukee SDC:n osajoukon ajoitusanalyysin asetuksiksi.
Kertoja kahdella vaiheella näyttää, miten sama netlista
on rikki tai kunnossa sen mukaan, mitä suunnittelija kertoo
analyysille: monisyklipolku on lupaus, jonka RTL:n on pidettävä.
Lupaus tarkistetaan simuloimalla (tp_kertoja2.v).
"""

import subprocess
import tempfile
from pathlib import Path

from sdc import lue_sdc
from sta import Analyysi, pahimmat
from synteesi import syntetisoi

HAK = Path(__file__).parent




# @alku lupaus
def tarkista_lupaus() -> str:
    """Simuloi RTL:n testipenkillä, joka mittaa, montako jaksoa tulot
    ovat olleet vakaina, kun tulos ladataan."""
    with tempfile.TemporaryDirectory() as tmp:
        sim = Path(tmp, "sim")
        subprocess.run(["iverilog", "-o", str(sim), str(HAK / "kertoja2.v"),
                        str(HAK / "tp_kertoja2.v")], check=True)
        ajo = subprocess.run(["vvp", "-n", str(sim)], check=True,
                             capture_output=True, text=True)
    return next(r for r in ajo.stdout.splitlines() if "latautui" in r)
# @loppu lupaus


def main() -> None:
    tulos = syntetisoi([HAK / "kertoja2.v"], "kertoja2")
    # @alku ajo
    for sdc in ["kertoja2.sdc", "kertoja2_mc.sdc"]:
        r = lue_sdc(HAK / sdc)
        polut = Analyysi(tulos, r).polut()
        asetus = pahimmat(polut, "asetus")[0]
        pito = pahimmat(polut, "pito")[0]
        print(f"{sdc}: jakso {r.jakso} ns, monisyklejä "
              f"{len(r.monisykli)}, vääriä polkuja {len(r.vaarat)}")
        print(f"  pahin asetus {asetus.alku} -> {asetus.loppu} "
              f"{asetus.marginaali:+.3f} ns")
        print(f"  pahin pito   {pito.alku} -> {pito.loppu} "
              f"{pito.marginaali:+.3f} ns")
        kertoja = pahimmat([p for p in polut if p.alku[:3] in
                            ("a_r", "b_r")], "asetus")[0]
        print(f"  kertojan pahin {kertoja.alku} -> {kertoja.loppu} "
              f"{kertoja.marginaali:+.3f} ns")
    print("RTL-simulointi: " + tarkista_lupaus())
    # @loppu ajo


if __name__ == "__main__":
    main()
