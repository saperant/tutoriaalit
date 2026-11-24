"""Parametroitu kuvaus: DMA-ohjain eri kanavamäärillä.

Sama kuvaus käännetään kolmella parametrin arvolla. Kanavakohtainen
rekisteriryhmä on taulukko, joten osoitteet lasketaan kuvauksesta
eikä käsin. Oma ominaisuus ``turvallinen`` kulkee mallin mukana.
"""

from __future__ import annotations

from systemrdl.rdltypes.typing import RDLValue

from kuvaus.kaanna import kaanna
from kuvaus.malli import rekisterit


def main() -> None:
    # @alku parametrit
    for kanavia in (None, 2, 16):
        parametrit: dict[str, RDLValue] | None = (
            None if kanavia is None else {"KANAVIA": kanavia})
        dma = kaanna("dma.rdl", parametrit)
        rek = rekisterit(dma)
        viimeinen = rek[-1]
        oletus = " (oletus)" if kanavia is None else ""
        arvo = dma.inst.parameters_dict["KANAVIA"].get_value()
        print(f"KANAVIA={arvo}{oletus}: {dma.size:#x} tavua, "
              f"{len(rek)} rekisteria")
        print(f"  viimeinen {viimeinen.polku} @ {viimeinen.osoite:#x}")
    # @loppu parametrit
    # @alku turvallinen
    dma = kaanna("dma.rdl")
    suojatut = [r.polku for r in rekisterit(dma) if r.turvallinen]
    print(f"turvallinen = true: {', '.join(suojatut)}")
    # @loppu turvallinen


if __name__ == "__main__":
    main()
