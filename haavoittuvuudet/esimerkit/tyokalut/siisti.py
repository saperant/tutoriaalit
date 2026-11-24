"""Siistii sanitoijan raakaraportin näytettäväksi: osoitteet,
prosessinumerot, polut ja koontitunnisteet korvataan, kirjastojen
sisäiset kehykset jätetään pois ja varjomuistin vedos lyhennetään.

Käyttö:  python3 siisti.py < raportti.txt
"""

from __future__ import annotations

import re
import sys
import textwrap

KORVAUKSET = [
    (re.compile(r"==\d+=="), "==PID=="),
    (re.compile(r"0x[0-9a-f]{6,}"), "0x..."),
    (re.compile(r"\(BuildId: [0-9a-f]+\)"), ""),
    (re.compile(r"(?:/[\w.+-]+)+/([\w.+-]+\.c)"), r"\1"),
    (re.compile(r"\((?:/[\w.+-]+)+/([\w.+-]+)\+0x\.\.\.\)"), r"(\1)"),
]
SISAISET = ("libsanitizer", "../sysdeps", "../csu", "in _start",
            "libc.so", "__libc_start")


def main() -> int:
    varjorivit = 0
    edellinen_osui = False
    for rivi in sys.stdin.read().splitlines():
        if any(s in rivi for s in SISAISET):
            continue
        for kuvio, korvaus in KORVAUKSET:
            rivi = kuvio.sub(korvaus, rivi)
        if rivi.startswith("  0x...:"):
            varjorivit += 1                 # vain kohdan ympäristö
            if varjorivit > 1 and not edellinen_osui:
                continue
        edellinen_osui = rivi.startswith("=>")
        if rivi.startswith("Shadow byte legend"):
            break
        print(textwrap.fill(rivi.rstrip(), width=76,
                            subsequent_indent="      ") if rivi.strip()
              else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
