"""SystemRDL-kuvauksen kääntäminen ja virheilmoitusten keruu.

Kääntäjän virheet kerätään listaksi muodossa ``tiedosto:rivi: virhe``,
jotta niitä voi verrata odotettuihin ja tulostaa ilman värikoodeja.
"""

from __future__ import annotations

from pathlib import Path

from systemrdl.compiler import RDLCompiler
from systemrdl.messages import MessagePrinter, RDLCompileError, Severity
from systemrdl.node import AddrmapNode
from systemrdl.rdltypes.typing import RDLValue
from systemrdl.source_ref import FileSourceRef, SourceRefBase

RDL = Path(__file__).resolve().parent.parent / "rdl"
TUOTETUT = RDL.parent / "tuotettu"


# @alku keraaja
class Keraaja(MessagePrinter):
    """Kerää kääntäjän viestit tulostamisen sijaan."""

    def __init__(self) -> None:
        super().__init__()
        self.viestit: list[str] = []

    def print_message(self, severity: Severity, text: str,
                      src_ref: SourceRefBase | None) -> None:
        paikka = ""
        if isinstance(src_ref, FileSourceRef):
            rivi = getattr(src_ref, "line", None)
            paikka = Path(src_ref.path).name
            paikka += f":{rivi}: " if rivi is not None else ": "
        self.viestit.append(f"{paikka}{severity.name.lower()}: {text}")
# @loppu keraaja


class KaannosVirhe(Exception):
    """Kuvaus ei kääntynyt. Viestit ovat attribuutissa ``viestit``."""

    def __init__(self, viestit: list[str]) -> None:
        super().__init__("\n".join(viestit))
        self.viestit = viestit


# @alku kaanna
def kaanna(tiedosto: str | Path,
           parametrit: dict[str, RDLValue] | None = None,
           ylin: str | None = None, rdl: Path = RDL) -> AddrmapNode:
    """Kääntää kuvauksen ja palauttaa ylimmän osoitekartan.

    Suhteellinen polku tulkitaan hakemistoon ``rdl``, josta myös
    sisällytettävät tiedostot etsitään.
    """
    polku = rdl / tiedosto
    keraaja = Keraaja()
    kaantaja = RDLCompiler(message_printer=keraaja)
    try:
        kaantaja.compile_file(str(polku), incl_search_paths=[str(rdl)])
        juuri = kaantaja.elaborate(top_def_name=ylin, parameters=parametrit)
    except RDLCompileError:
        raise KaannosVirhe(keraaja.viestit) from None
    return juuri.top
# @loppu kaanna
