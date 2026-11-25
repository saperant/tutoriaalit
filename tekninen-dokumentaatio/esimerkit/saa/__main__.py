"""Komentorivikäyttö: ``python3 -m saa``."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from saa.lukema import LukemaVirhe, jasenna_rivi
from saa.tilasto import yhteenveto


def jasennin() -> argparse.ArgumentParser:
    """Rakentaa komentorivin jäsentimen."""
    p = argparse.ArgumentParser(
        prog="saa", description="Laskee aseman lukemista yhteenvedon.")
    p.add_argument("tiedosto", type=Path,
                   help="lukemarivit, yksi rivi lukemaa kohden")
    p.add_argument("--asema", required=True, help="aseman tunnus")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    """Ajaa komentoriviohjelman.

    Args:
        argv: Argumentit ilman ohjelman nimeä tai ``None``, jolloin
            käytetään komentorivin argumentteja.

    Returns:
        Paluuarvo: 0 onnistui, 1 virheellinen rivi tai tuntematon
        asema.
    """
    args = jasennin().parse_args(argv)
    try:
        lukemat = [jasenna_rivi(rivi) for rivi
                   in args.tiedosto.read_text("utf-8").splitlines() if rivi]
    except LukemaVirhe as virhe:
        print(f"virhe: {virhe}", file=sys.stderr)
        return 1
    tulos = yhteenveto(args.asema, lukemat)
    if tulos is None:
        print(f"virhe: asemalta {args.asema} ei ole lukemia",
              file=sys.stderr)
        return 1
    print(f"{tulos.asema}: {tulos.maara} lukemaa, "
          f"{tulos.alin_c:+.1f} ... {tulos.ylin_c:+.1f} C, "
          f"keskiarvo {tulos.keskiarvo_c:+.1f} C")
    return 0


if __name__ == "__main__":
    sys.exit(main())
