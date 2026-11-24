#!/usr/bin/env bash
# Sama ohjelma ilman .cfi-direktiivejä: purkaja ei pääse assembly-
# funktion ohi, eikä main-kehystä löydy.
set -euo pipefail
hak=$(dirname "$0")
lahteet=("$hak/main.c")
# shellcheck disable=SC2086
"$CC_X86" $CFLAGS -static -o "$RAK/x86-ei-cfi" "${lahteet[@]}" "$hak/x86.S"
# shellcheck disable=SC2086
"$CC_RV" $CFLAGS -static -o "$RAK/rv-ei-cfi" "${lahteet[@]}" "$hak/rv.S"
echo "x86 ilman CFI:"
"$RAK/x86-ei-cfi"
echo "rv ilman CFI:"
qemu-riscv64 "$RAK/rv-ei-cfi"
