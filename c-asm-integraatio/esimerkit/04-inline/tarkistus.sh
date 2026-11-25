#!/usr/bin/env bash
# Mitä käskyjä kumpaankin funktioon jäi -O2:lla käännettäessä.
set -euo pipefail
# @alku kaskyt
kaskyt() { # OBJDUMP OHJELMA FUNKTIO
    "$1" -d --no-show-raw-insn --disassemble="$3" "$2" |
        sed -nE 's/^ +[0-9a-f]+:\t/    /p' | tr -s ' \t' ' ' | sed 's/^/   /'
}
for f in ilman_volatile volatilen_kanssa; do
    echo "$f, x86:"
    kaskyt objdump "$RAK/x86" "$f"
    echo "$f, rv:"
    kaskyt "$OBJDUMP_RV" "$RAK/rv" "$f"
done
# @loppu kaskyt
