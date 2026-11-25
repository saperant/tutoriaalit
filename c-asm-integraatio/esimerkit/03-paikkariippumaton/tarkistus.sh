#!/usr/bin/env bash
# Sama ohjelma ilman -static-valitsinta. Kääntäjän oletus on
# paikkariippumaton ohjelma (PIE), johon absoluuttinen osoite ei kelpaa.
set -euo pipefail
hak=$(dirname "$0")

# @alku pie
# Oikea versio: linkittyy PIE:ksi ja toimii.
# shellcheck disable=SC2086
"$CC_X86" $CFLAGS -o "$RAK/x86-pie" "$hak/main.c" "$hak/x86.S"
readelf -hW "$RAK/x86-pie" | grep -o 'DYN (.*)' | sed 's/^/x86 /'
"$RAK/x86-pie" | sed 's/^/x86 /'
# shellcheck disable=SC2086
"$CC_RV" $CFLAGS -o "$RAK/rv-pie" "$hak/main.c" "$hak/rv.S"
qemu-riscv64 -L /usr/riscv64-linux-gnu "$RAK/rv-pie" | sed 's/^/rv  /'
# @loppu pie

# @alku absoluuttinen
# Absoluuttinen osoite: linkkeri hylkää. Viestistä näytetään ydin.
for ark in x86 rv; do
    if [[ $ark == x86 ]]; then cc=$CC_X86; else cc=$CC_RV; fi
    # shellcheck disable=SC2086
    if "$cc" $CFLAGS -DABSOLUUTTINEN -o "$RAK/$ark-abs" "$hak/main.c" \
        "$hak/$ark.S" 2> "$RAK/$ark-abs.txt"; then
        echo "$ark: linkittyi, vaikka ei pitänyt"
        exit 1
    fi
    printf '%-3s ' "$ark"
    grep -o 'relocation R_[A-Z0-9_]* against .*laskuri. can not be used' \
        "$RAK/$ark-abs.txt" | tr -d '`'"'" | sed 's/ symbol//' | head -n 1
done
# @loppu absoluuttinen

# @alku relokaatiot
# Mitä kokoaja pyytää linkkeriltä oikeassa versiossa.
"$CC_X86" -c -o "$RAK/x86.o" "$hak/x86.S"
readelf -rW "$RAK/x86.o" | awk '/R_X86/ {print "x86", $3, $5}'
"$CC_RV" -c -o "$RAK/rv.o" "$hak/rv.S"
"$READELF_RV" -rW "$RAK/rv.o" |
    awk '/R_RISCV/ && !/RELAX/ {print "rv ", $3, $5}'
# @loppu relokaatiot
