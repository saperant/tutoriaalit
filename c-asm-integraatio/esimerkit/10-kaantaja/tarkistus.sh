#!/usr/bin/env bash
set -euo pipefail
# @alku pura
pura() { # OBJDUMP OHJELMA FUNKTIO
    "$1" -d --no-show-raw-insn --disassemble="$3" "$2" |
        sed -nE 's/^ +[0-9a-f]+:\t//p' | tr -s ' \t' ' ' |
        sed 's/^/    /'
}
for f in jaa_kymmenella vakio_c vakio_asm; do
    echo "$f, x86:"
    pura objdump "$RAK/x86" "$f"
    echo "$f, rv:"
    pura "$OBJDUMP_RV" "$RAK/rv" "$f"
done
# @loppu pura
