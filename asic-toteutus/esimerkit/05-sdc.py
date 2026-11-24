"""SDC-rajoitteet: kello, tulojen ja lähtöjen viiveet, monisyklipolku.

Pieni jäsennin lukee SDC:n (Tcl-syntaksia) osajoukon ajoitusanalyysin
asetuksiksi. Kertoja kahdella vaiheella näyttää, miten sama netlista
on rikki tai kunnossa sen mukaan, mitä suunnittelija kertoo
analyysille: monisyklipolku on lupaus, jonka RTL:n on pidettävä.
"""

import re
from pathlib import Path

from sta import Analyysi, Rajoitteet, pahimmat
from synteesi import syntetisoi

HAK = Path(__file__).parent


# @alku jasennin
def valinta(args: list[str], lippu: str) -> list[str]:
    """Lipun jälkeisen [get_cells {...}]-valinnan nimimallit."""
    if lippu not in args:
        return ["*"]
    kohde = args[args.index(lippu) + 1].strip("[]")
    return re.findall(r"[\w*\[\]]+", kohde)[1:]       # ohita get_*


def lue_sdc(polku: Path) -> Rajoitteet:
    """Jäsentää SDC-osajoukon. Solut nimetään rekisterin nimellä."""
    r = Rajoitteet(jakso=0.0)
    teksti = polku.read_text("utf-8").replace("\\\n", " ")
    for rivi in teksti.splitlines():
        rivi = rivi.split("#")[0].strip()
        if not rivi:
            continue
        osat = re.findall(r"\[[^\]]*\]|\{[^}]*\}|\S+", rivi)
        komento, args = osat[0], osat[1:]

        if komento == "source":
            r = lue_sdc(polku.with_name(args[0]))
        elif komento == "create_clock":
            r.jakso = float(args[args.index("-period") + 1])
            r.kello = args[args.index("-name") + 1]
        elif komento == "set_clock_uncertainty":
            r.epavarmuus = float(args[0])
        elif komento == "set_input_delay":
            r.sisaan = float(args[0])
        elif komento == "set_output_delay":
            r.ulos = float(args[0])
        elif komento == "set_input_transition":
            r.tulon_slew = float(args[0])
        elif komento == "set_load":
            r.kuorma_ulos = float(args[0])
        elif komento == "set_multicycle_path" and "-setup" in args:
            r.monisykli += [(a, b, int(args[0]))
                            for a in valinta(args, "-from")
                            for b in valinta(args, "-to")]
        elif komento == "set_false_path":
            r.vaarat += [(a, b) for a in valinta(args, "-from")
                         for b in valinta(args, "-to")]
    return r
# @loppu jasennin


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
    # @loppu ajo


if __name__ == "__main__":
    main()
