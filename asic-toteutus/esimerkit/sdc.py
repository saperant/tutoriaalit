"""SDC-rajoitteiden (Tcl-syntaksia) osajoukon jäsennin.

Lukee kellon, epävarmuuden, tulo- ja lähtöviiveet, kuorman sekä
monisykli- ja väärät polut opetusanalyysin asetuksiksi (sta.py).
"""

import re
from pathlib import Path

from sta import Rajoitteet


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
    # @alku kaytto
    r = lue_sdc(Path(__file__).with_name("kertoja2_mc.sdc"))
    print(f"kello {r.kello}: jakso {r.jakso} ns, epävarmuus "
          f"{r.epavarmuus} ns")
    print(f"tulot {r.sisaan} ns, lähdöt {r.ulos} ns, kuorma "
          f"{r.kuorma_ulos * 1000:.0f} fF")
    for alku, loppu, n in r.monisykli:
        print(f"monisykli {n}: {alku} -> {loppu}")
    for alku, loppu in r.vaarat:
        print(f"väärä polku: {alku} -> {loppu}")
    # @loppu kaytto


if __name__ == "__main__":
    main()
