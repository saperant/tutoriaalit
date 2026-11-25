"""Lähdeluettelo yhdestä paikasta: jokaisen työkalun komentorivi
tuotetaan samasta kuvauksesta, ja luettelo tarkistetaan ennen ajoa."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from vuo.lahteet import icarus, lue, verilator_lint, yosys_luku

JUURI = Path(__file__).resolve().parent


def nayta(komento: list[str], tmp: str) -> None:
    """Tulostaa komennon: valitsimet yhdelle riville, lähteet toiselle.
    Polut näytetään suhteessa projektin juureen."""
    sanat = [s.replace(f"{JUURI}/", "").replace(f"{tmp}/", "")
             for s in komento]
    lahteet = [s for s in sanat if s.endswith(".sv")]
    print("  " + " ".join(s for s in sanat if s not in lahteet))
    print("      " + " ".join(lahteet))


# @alku kokeet
def main() -> None:
    kohteet = lue(JUURI / "asetukset" / "lahteet.toml", JUURI)
    with tempfile.TemporaryDirectory() as tmp:
        for k in kohteet.values():
            lint = verilator_lint(k)
            sim = icarus(k, Path(tmp) / f"{k.nimi}.vvp")
            print(f"[{k.nimi}]")
            nayta(lint, tmp)
            nayta(sim, tmp)
            for rivi in yosys_luku(k):
                print("  yosys:", rivi.replace(f"{JUURI}/", ""))
            # Komennot myös ajetaan: molemmat työkalut hyväksyvät saman
            # luettelon.
            tulokset = [subprocess.run(c, capture_output=True).returncode
                        for c in (lint, sim)]
            print("  paluuarvot (lint, icarus):", tulokset)

        rikki = Path(tmp) / "rikki.toml"
        rikki.write_text('[x]\nylin = "x"\n'
                         'lahteet = ["rtl/alu.sv", "rtl/puuttuu.sv"]\n')
        try:
            lue(rikki, JUURI)
        except ValueError as virhe:
            print("hylätty:", virhe)
# @loppu kokeet


if __name__ == "__main__":
    main()
