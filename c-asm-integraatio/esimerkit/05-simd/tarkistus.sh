#!/usr/bin/env bash
# Vektoroiko kääntäjä skalaariversion itse? Lasketaan käskyt ja
# niistä vektorikäskyt (x86: xmm/ymm-rekisterit, RISC-V: v-alkuiset).
set -euo pipefail
hak=$(dirname "$0")
# @alku automaattinen
kaskyt() { # OBJDUMP OBJEKTI
    "$1" -d --no-show-raw-insn "$2" | sed -nE 's/^ +[0-9a-f]+:\t//p'
}
for o in -O2 -O3; do
    "$CC_X86" "$o" -c -o "$RAK/x86.o" "$hak/skalaari.c"
    "$CC_RV" "$o" -march=rv64gcv -c -o "$RAK/rv.o" "$hak/skalaari.c"
    x86=$(kaskyt objdump "$RAK/x86.o")
    rv=$(kaskyt "$OBJDUMP_RV" "$RAK/rv.o")
    echo "x86 $o: käskyjä $(wc -l <<< "$x86")," \
        "vektorikäskyjä $(grep -cE '%[xy]mm' <<< "$x86" || true)"
    echo "rv  $o: käskyjä $(wc -l <<< "$rv")," \
        "vektorikäskyjä $(grep -cE '^v' <<< "$rv" || true)"
done
# @loppu automaattinen
