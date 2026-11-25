#!/usr/bin/env bash
# Punainen vyöhyke konekoodissa ja sama ohjelma ilman vyöhykettä.
set -euo pipefail
hak=$(dirname "$0")
# @alku purettu
echo "liput_rikki, -O2:"
objdump -d --no-show-raw-insn --disassemble=liput_rikki "$RAK/x86" |
    sed -nE 's/^ +[0-9a-f]+:\t/    /p' | tr -s ' \t' ' ' | sed 's/^/   /'
# @loppu purettu
# @alku ilman
# Ydin ja muu keskeytyksiä käsittelevä koodi käännetään näin: kääntäjä
# siirtää pino-osoitinta aina, eikä vyöhykettä ole.
# shellcheck disable=SC2086
"$CC_X86" $CFLAGS -mno-red-zone -DEI_VYOHYKETTA -static \
    -o "$RAK/x86-ei-vyohyketta" "$hak/main.c"
echo "-mno-red-zone:"
"$RAK/x86-ei-vyohyketta"
# @loppu ilman
