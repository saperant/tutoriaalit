#!/usr/bin/env bash
# Sama ohjelma -O0:lla: virheet eivät näy, koska kääntäjä lukee ja
# kirjoittaa jokaisen muuttujan muistin kautta.
set -euo pipefail
hak=$(dirname "$0")
"$CC_X86" -O0 -std=c17 -static -o "$RAK/x86-O0" "$hak/main.c"
echo "x86 -O0:"
"$RAK/x86-O0"
# @alku purettu
echo "ilman_et, x86 -O2 (kolme ensimmäistä käskyä):"
objdump -d --no-show-raw-insn --disassemble=ilman_et "$RAK/x86" |
    sed -nE 's/^ +[0-9a-f]+:\t/    /p' | tr -s ' \t' ' ' |
    sed -n 's/^/   /; 1,3p'
# @loppu purettu
