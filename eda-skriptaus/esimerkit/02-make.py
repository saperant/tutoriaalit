"""Sama vuo Makella: muutosajat ratkaisevat, eivät sisältö eikä
parametrit."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

JUURI = Path(__file__).resolve().parent


# @alku make
def make(projekti: Path,
         *argumentit: str) -> subprocess.CompletedProcess[str]:
    # Ulomman Maken valitsimet (-j, -s, jobserver) eivät kuulu tälle.
    env = {k: v for k, v in os.environ.items()
           if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL")}
    return subprocess.run(
        ["make", "-f", str(JUURI / "vuo.mk"), f"JUURI={projekti}",
         f"AJO={projekti / 'ajo'}", *argumentit],
        capture_output=True, text=True, env=env, check=False)


def kysy(otsikko: str, projekti: Path, *argumentit: str) -> None:
    """make -q ei aja mitään: paluuarvo 0 = ajan tasalla."""
    tulos = make(projekti, "-q", *argumentit)
    tila = "ajan tasalla" if tulos.returncode == 0 else "vanhentunut"
    print(f"{otsikko}: {tila}")
# @loppu make


# @alku kokeet
def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        projekti = Path(tmp)
        for hak in ("rtl", "tcl"):
            shutil.copytree(JUURI / hak, projekti / hak)
        print("make:")
        print(make(projekti).stdout, end="")
        kysy("ilman muutoksia", projekti)
        kysy("LEVEYS=16", projekti, "LEVEYS=16")
        # touch; aika on tulevaisuudessa, ettei kellon tarkkuus ratkaise.
        uusi = time.time() + 10
        os.utime(projekti / "rtl" / "laskuri.sv", (uusi, uusi))
        kysy("touch rtl/laskuri.sv", projekti)
        print("make:")
        print(make(projekti).stdout, end="")
# @loppu kokeet


if __name__ == "__main__":
    main()
