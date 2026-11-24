"""Laitepuun solmut järjestelmäpiirin kuvauksesta.

Linux ja muut käyttöjärjestelmät löytävät oheislaitteet laitepuusta:
solmun ``reg`` kertoo osoitealueen, ``interrupts`` keskeytyksen ja
``compatible`` sen, mikä ajuri laitteeseen sidotaan. Kaikki kolme
tulevat samasta kuvauksesta kuin RTL ja C-otsakkeet.
"""

from __future__ import annotations

from systemrdl.node import AddrmapNode


# @alku solmut
def solmut(ylin: AddrmapNode) -> str:
    rivit = ["/* Tuotettu SystemRDL-kuvauksesta. Ala muokkaa kasin. */"]
    for lapsi in ylin.children():
        if not isinstance(lapsi, AddrmapNode):
            continue
        yhteensopiva = lapsi.get_property("yhteensopiva")
        if yhteensopiva is None:
            continue  # ei ohjelmiston näkyvä laite
        osoite = lapsi.absolute_address
        nimi = (lapsi.orig_type_name or lapsi.inst_name).lower()
        rivit += [
            "",
            f"{lapsi.inst_name.lower()}: {nimi}@{osoite:x} {{",
            f'    compatible = "{yhteensopiva}";',
            f"    reg = <0x{osoite:08x} 0x{lapsi.size:x}>;"]
        nro = lapsi.get_property("keskeytys")
        if nro is not None:
            rivit.append(f"    interrupts = <{nro}>;")
        rivit.append("};")
    return "\n".join(rivit) + "\n"
# @loppu solmut
