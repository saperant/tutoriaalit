"""lokityokalu: simulaatiolokien yhteenveto ja suodatus.

  lokityokalu yhteenveto [TIEDOSTO ...]
  lokityokalu virheet [--taso T] [--komponentti K] [TIEDOSTO ...]

Ilman tiedostoja tai tiedostonimellä '-' luetaan syötettä, joten työkalu
sopii putken osaksi. Tulokset menevät tulosteeseen, diagnostiikka
virhetulosteeseen. Paluuarvo: 0 kunnossa, 1 lokissa on virheitä
(--tiukka), 2 virheellinen komentorivi.
"""

import argparse
import logging
import os
import sys
from collections import Counter
from collections.abc import Iterator, Sequence
from pathlib import Path

TASOT = ("INFO", "WARNING", "ERROR", "FATAL")
loki = logging.getLogger("lokityokalu")


def rivit(nimet: Sequence[str]) -> Iterator[tuple[str, str]]:
    """Antaa (lähde, rivi)-parit tiedostoista tai syötteestä."""
    for nimi in nimet or ["-"]:
        if nimi == "-":
            yield from (("-", r) for r in sys.stdin)
            continue
        loki.debug("luetaan %s", nimi)
        with Path(nimi).open(encoding="utf-8", errors="replace") as f:
            yield from ((nimi, r) for r in f)


def jasenna(rivi: str) -> tuple[str, str, str] | None:
    osat = rivi.split(maxsplit=5)
    if len(osat) < 6 or osat[0] != "@" or osat[3] not in TASOT:
        return None
    return osat[3], osat[4].rstrip(":"), osat[5].rstrip("\n")


# @alku komennot
def yhteenveto(args: argparse.Namespace) -> int:
    tasot: Counter[str] = Counter()
    for _, rivi in rivit(args.tiedostot):
        if (tulos := jasenna(rivi)) is not None:
            tasot[tulos[0]] += 1
    for taso in TASOT:
        print(f"{taso:<8}{tasot[taso]:>5}")
    virheita = tasot["ERROR"] + tasot["FATAL"]
    if virheita and args.tiukka:
        loki.error("lokissa on %d virhettä", virheita)
        return 1
    return 0


def virheet(args: argparse.Namespace) -> int:
    kynnys = TASOT.index(args.taso)
    for lahde, rivi in rivit(args.tiedostot):
        tulos = jasenna(rivi)
        if tulos is None or TASOT.index(tulos[0]) < kynnys:
            continue
        if args.komponentti and tulos[1] != args.komponentti:
            continue
        print(f"{lahde}: {tulos[0]} {tulos[1]}: {tulos[2]}")
    return 0
# @loppu komennot


# @alku jasennin
def tee_jasennin() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="lokityokalu", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-v", "--verbose", action="count", default=0,
                   help="lisää diagnostiikkaa (toistettavissa)")
    alikomennot = p.add_subparsers(dest="komento", required=True)

    y = alikomennot.add_parser("yhteenveto", help="viestit tasoittain")
    y.add_argument("--tiukka", action="store_true",
                   help="paluuarvo 1, jos lokissa on virheitä")
    y.set_defaults(toiminto=yhteenveto)

    v = alikomennot.add_parser("virheet", help="suodata viestit")
    v.add_argument("--taso", choices=TASOT[1:], default="ERROR",
                   help="vähimmäistaso (oletus: %(default)s)")
    v.add_argument("--komponentti", metavar="NIMI")
    v.set_defaults(toiminto=virheet)

    for ali in (y, v):
        ali.add_argument("tiedostot", nargs="*", metavar="TIEDOSTO",
                         help="lokitiedostot; '-' tai ei mitään = syöte")
    return p
# @loppu jasennin


# @alku main
def main(argv: Sequence[str] | None = None) -> int:
    args = tee_jasennin().parse_args(argv)
    logging.basicConfig(
        stream=sys.stderr, format="%(name)s: %(levelname)s: %(message)s",
        level=logging.DEBUG if args.verbose else logging.WARNING)
    try:
        tulos: int = args.toiminto(args)
    except BrokenPipeError:
        # Esim. `lokityokalu ... | head`: lukija sulki putken. Ohjataan
        # loput tulosteesta /dev/nulliin, ettei Python valita lopussa.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 1
    except OSError as e:  # BrokenPipeError on OSError, siksi tämä toisena
        loki.error("%s", e)
        return 2
    return tulos


if __name__ == "__main__":
    sys.exit(main())
# @loppu main
