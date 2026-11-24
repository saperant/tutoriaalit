"""Ulkoisten työkalujen ajaminen esimerkeistä.

Verilator kutsuu käännöksessä Makea. Ulomman Maken MAKEFLAGS (esim.
rinnakkaisuus ja jobserver) poistetaan, jotta sisempi Make ei peri
niitä.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def aja(komento: list[str], hakemisto: Path | None = None,
        sallittu_virhe: bool = False) -> subprocess.CompletedProcess[str]:
    """Ajaa komennon ja palauttaa tulosteen. Virhe kaataa esimerkin,
    ellei sitä ole sallittu (esim. tahallaan rikottu syöte)."""
    ymparisto = {k: v for k, v in os.environ.items()
                 if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL")}
    tulos = subprocess.run(komento, cwd=hakemisto, env=ymparisto,
                           capture_output=True, text=True, check=False)
    if tulos.returncode != 0 and not sallittu_virhe:
        raise RuntimeError(f"{komento[0]} epäonnistui:\n{tulos.stdout}"
                           f"{tulos.stderr}")
    return tulos
