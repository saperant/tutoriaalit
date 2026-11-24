#!/usr/bin/env bash
# Pinon tasauksen rikkominen x86-64:llä: ohjelma kaatuu vasta
# kutsutussa funktiossa, kaukana virheen paikasta.
set -euo pipefail
# @alku kaatuu
koodi=0
{ "$RAK/x86" tasaus; } 2> /dev/null || koodi=$?
if ((koodi > 128)); then
    echo "kaatui signaaliin $(kill -l $((koodi - 128)))"
else
    echo "paluuarvo $koodi"
fi
# @loppu kaatuu
echo "kayttaa_vektoria:"
objdump -d --no-show-raw-insn --disassemble=kayttaa_vektoria \
    "$RAK/x86" | sed -nE 's/^ +[0-9a-f]+:\t/    /p' | tr -s ' \t' ' ' |
    sed 's/^/   /'
