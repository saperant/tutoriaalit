#!/usr/bin/env bash
# Mihin kääntäjä muuttaa __builtin_popcountll- ja __builtin_bswap64-
# kutsut eri kohdeprosessoreille.
set -euo pipefail
hak=$(dirname "$0")
# @alku kohteet
toteutus() { # OBJDUMP OBJEKTI FUNKTIO
    local d k
    d=$("$1" -dr --no-show-raw-insn --disassemble="$3" "$2")
    k=$(sed -nE 's/^ +[0-9a-f]+:\t//p' <<< "$d")
    if grep -q 'R_.*_PLT' <<< "$d"; then
        echo "kirjastokutsu" \
            "$(grep -oE 'PLT(32)?\s+[a-z_0-9]+' <<< "$d" | awk '{print $2}')"
    else
        awk '{print $1}' <<< "$k" | paste -sd ' '
    fi
}
kohde() { # NIMI KÄÄNTÄJÄ OBJDUMP VALITSIMET...
    local nimi=$1 cc=$2 od=$3
    shift 3
    "$cc" -O2 "$@" -c -o "$RAK/b.o" "$hak/bitit.c"
    echo "$nimi"
    echo "  ykkosia: $(toteutus "$od" "$RAK/b.o" ykkosia)"
    echo "  kaanna:  $(toteutus "$od" "$RAK/b.o" kaanna)"
}
kohde "x86-64 (perustaso)" "$CC_X86" objdump
kohde "x86-64 -mpopcnt" "$CC_X86" objdump -mpopcnt
kohde "RISC-V rv64gc" "$CC_RV" "$OBJDUMP_RV" -march=rv64gc
kohde "RISC-V rv64gc_zbb" "$CC_RV" "$OBJDUMP_RV" -march=rv64gc_zbb
# @loppu kohteet
