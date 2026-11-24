#!/usr/bin/env bash
# Symbolitaulu: mitä FUNKTIO- ja LOPPU-makrot tuottavat
# objektitiedostoon (koko, tyyppi, sidonta, näkyvyys).
set -euo pipefail
hak=$(dirname "$0")
# @alku symbolit
symboli() { # NIMIÖ READELF OBJEKTI
    "$2" -sW "$3" | awk -v n="$1" '$8 == "laske" {
        print n, "koko", $3, $4, $5, $6, $8 }'
}
"$CC_X86" -c -o "$RAK/x86.o" "$hak/x86.S"
symboli x86: readelf "$RAK/x86.o"
"$CC_RV" -c -o "$RAK/rv.o" "$hak/rv.S"
symboli "rv: " "$READELF_RV" "$RAK/rv.o"
# @loppu symbolit
