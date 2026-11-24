"""Työkalujen ajaminen eräajona: komento, loki ja paluuarvo."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

# @alku ajo
AIKAKATKAISU = -1
# Ulomman Maken jobserver-tiedot eivät kuulu työkalun omalle Makelle
# (Verilator kutsuu Makea itse).
POISTETTAVAT = ("MAKEFLAGS", "MFLAGS", "MAKELEVEL")


@dataclass(frozen=True)
class Ajo:
    """Yhden työkaluajon tulos. Tuloste on lokitiedostossa."""

    komento: tuple[str, ...]
    paluuarvo: int
    loki: Path

    @property
    def onnistui(self) -> bool:
        return self.paluuarvo == 0


def aja(komento: list[str], loki: Path, *, hakemisto: Path | None = None,
        aikaraja: float = 600.0,
        ymparisto: dict[str, str] | None = None) -> Ajo:
    """Ajaa työkalun ilman kuorta ja ohjaa tulosteen lokiin.

    Lokin ensimmäinen rivi on ajettu komento, jotta ajon voi toistaa
    käsin. Aikakatkaisu ei kaada vuota vaan näkyy paluuarvona.
    """
    loki.parent.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k not in POISTETTAVAT}
    env.update(ymparisto or {})
    with loki.open("w", encoding="utf-8") as f:
        f.write("$ " + " ".join(komento) + "\n")
        f.flush()
        try:
            tulos = subprocess.run(komento, cwd=hakemisto, env=env,
                                   stdout=f, stderr=subprocess.STDOUT,
                                   timeout=aikaraja, check=False)
            koodi = tulos.returncode
        except subprocess.TimeoutExpired:
            f.write(f"\n*** aikakatkaisu {aikaraja:g} s\n")
            koodi = AIKAKATKAISU
    return Ajo(tuple(komento), koodi, loki)
# @loppu ajo


# @alku versio
def tyokaluversio(komento: list[str]) -> str:
    """Työkalun versiorivi, joka tallennetaan ajon tietoihin."""
    try:
        tulos = subprocess.run(komento, capture_output=True, text=True,
                               timeout=30, check=False)
    except FileNotFoundError:
        return "puuttuu"
    except subprocess.TimeoutExpired:
        return "tuntematon"
    rivit = (tulos.stdout or tulos.stderr).strip().splitlines()
    return rivit[0] if rivit else "tuntematon"
# @loppu versio
