"""Kirjoittaa mallin vakiot RTL:n käyttöön.

Käyttö: python3 -m malli.generoi [--tarkista]

Tuottaa tiedostot rtl/kertoimet.svh (kertoimet pakattuina vakioina),
rtl/cordic_kulmat.svh (CORDICin kulmataulukko funktiona) ja
rtl/nco_sini.hex ($readmemh-muotoinen sinitaulukko). Valitsimella
--tarkista tiedostoja ei kirjoiteta, vaan paluuarvo on 1, jos ne
poikkeavat generoidusta.
Generoidut tiedostot ovat versionhallinnassa, jotta RTL:n voi lukea ja
syntetisoida ilman Pythonia; testi varmistaa, etteivät ne vanhene.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

from malli.kertoimet import (
    CORDIC_ZW,
    FIR,
    KERROIN_BITIT,
    NCO_BITIT,
    POLYFAASI,
    SOS,
    cordic_kulmat,
    nco_taulukko,
)

RTL = Path(__file__).resolve().parent.parent / "rtl"


# @alku pakkaa
def pakkaa(arvot: Sequence[int], bitit: int) -> str:
    """Kertoimet yhdeksi pakatuksi vakioksi: alkio 0 alimpina bitteinä,
    jolloin RTL lukee alkion i lausekkeella K[i*KW +: KW]."""
    maski = (1 << bitit) - 1
    osat = [f"{bitit}'h{a & maski:0{(bitit + 3) // 4}x}" for a in arvot]
    return "{" + ", ".join(reversed(osat)) + "}"
    # @loppu pakkaa


def rivita(nimi: str, arvo: str) -> list[str]:
    """`define NIMI {...}, rivitettynä kenoviivoin."""
    palat = arvo.strip("{}").split(", ")
    rivit = [f"`define {nimi} {{ \\"]
    for i in range(0, len(palat), 4):
        loppu = ", \\" if i + 4 < len(palat) else " \\"
        rivit.append("  " + ", ".join(palat[i : i + 4]) + loppu)
    rivit.append("}")
    return rivit


def kertoimet_svh() -> str:
    rivit = [
        "// GENEROITU: python3 -m malli.generoi. Älä muokkaa käsin.",
        "// Kertoimet pakattuina vakioina, alkio 0 alimpina bitteinä.",
        "`ifndef KERTOIMET_SVH",
        "`define KERTOIMET_SVH",
        "",
        *rivita("FIR_KERTOIMET", pakkaa(FIR, KERROIN_BITIT)),
        "",
        *rivita("POLYFAASI_KERTOIMET", pakkaa(POLYFAASI, KERROIN_BITIT)),
        "",
    ]
    for i, lohko in enumerate(SOS):
        rivit += [f"`define SOS{i}_KERTOIMET {pakkaa(lohko, 16)}"]
    rivit += ["", "`endif"]
    return "\n".join(rivit) + "\n"


def cordic_svh() -> str:
    """Kulmataulukko funktiona. Tiedosto sisällytetään moduulin sisään,
    joten siinä ei ole include-suojaa."""
    rivit = [
        "// GENEROITU: python3 -m malli.generoi. Älä muokkaa käsin.",
        "// CORDIC: atan(2**-i), täysi kierros = 2**18.",
        f"function automatic logic signed [{CORDIC_ZW - 1}:0] "
        "cordic_kulma(input int i);",
        "  case (i)",
    ]
    for i, k in enumerate(cordic_kulmat()):
        rivit.append(f"    {i}: cordic_kulma = {CORDIC_ZW}'sd{k};")
    rivit += [
        f"    default: cordic_kulma = {CORDIC_ZW}'sd0;",
        "  endcase",
        "endfunction",
    ]
    return "\n".join(rivit) + "\n"


def sini_hex() -> str:
    leveys = (NCO_BITIT + 3) // 4
    return "".join(f"{v:0{leveys}x}\n" for v in nco_taulukko())


def main() -> int:
    tarkista = "--tarkista" in sys.argv[1:]
    virheita = 0
    for nimi, sisalto in (
        ("kertoimet.svh", kertoimet_svh()),
        ("cordic_kulmat.svh", cordic_svh()),
        ("nco_sini.hex", sini_hex()),
    ):
        polku = RTL / nimi
        if not tarkista:
            polku.write_text(sisalto, "utf-8")
        elif not polku.exists() or polku.read_text("utf-8") != sisalto:
            print(f"rtl/{nimi}: vanhentunut, aja python3 -m malli.generoi")
            virheita += 1
    if tarkista and not virheita:
        print("OK: generoidut tiedostot ajan tasalla")
    return 1 if virheita else 0


if __name__ == "__main__":
    sys.exit(main())
