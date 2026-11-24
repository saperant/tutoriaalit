"""Ajurin koon valinta: viive ja siirtymäaika haarautumisen funktiona.

Solun viive riippuu kahdesta asiasta: tulon siirtymäajasta (slew) ja
lähdön kuormasta. Heikko ajuri (INV_X1) on nopea pienellä kuormalla,
mutta sen viive ja lähdön siirtymäaika kasvavat kuorman mukana.
Vahva puskuri (BUF_X4) maksaa enemmän pinta-alaa ja kuormittaa
edellistä astetta, mutta kestää suuren haarautumisen.
"""

from pathlib import Path

from liberty import Ryhma, lue, taulukko

KIRJASTO = lue(Path(__file__).with_name("opetus.lib"))


# @alku viive
def viive(solu: str, slew: float, kuorma: float) -> tuple[float, float]:
    """Hitaampi reuna: (viive, lähdön siirtymäaika) ns."""
    s: Ryhma = KIRJASTO.yksi("cell", solu)
    lahto = next(p for p in s.kaikki("pin")
                 if p.attr["direction"] == "output")
    kaari = lahto.kaikki("timing")[0]

    def arvo(nimi: str) -> float:
        return taulukko(KIRJASTO, kaari.yksi(nimi, "nldm_3x3")).arvo(
            slew, kuorma)

    return (max(arvo("cell_rise"), arvo("cell_fall")),
            max(arvo("rise_transition"), arvo("fall_transition")))
# @loppu viive


def main() -> None:
    # @alku vertailu
    nand_c = float(KIRJASTO.yksi("cell", "NAND2_X1").yksi("pin", "A")
                   .attr["capacitance"])
    print("haarautuma  INV_X1 viive/slew   BUF_X4 viive/slew  (ns)")
    for n in [1, 4, 8, 16, 32]:
        kuorma = n * nand_c + 0.001 * (1 + n)     # pinnit + johdin
        iv, isl = viive("INV_X1", 0.10, kuorma)
        bv, bsl = viive("BUF_X4", 0.10, kuorma)
        print(f"{n:10}  {iv:7.3f} / {isl:5.3f}     "
              f"{bv:7.3f} / {bsl:5.3f}")
    # @loppu vertailu


if __name__ == "__main__":
    main()
