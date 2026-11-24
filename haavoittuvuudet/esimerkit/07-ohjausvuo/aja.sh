#!/usr/bin/env bash
# Ohjausvuon eheys: Clangin CFI sekä CET- ja PAC-käskyt.
source ./yhteinen.sh
LLD=$(command -v ld.lld-20 || command -v ld.lld)

otsikko "CFI: tyyppisekaannus epäsuorassa kutsussa"
# @alku cfi
"$CLANG" -std=c23 -O1 -g -flto -fvisibility=hidden -fsanitize=cfi \
    -fno-sanitize-trap=cfi --ld-path="$LLD" lisaosat.c -o lisaosat
./lisaosat tervehdi
kaatuu ./lisaosat celsius
# @loppu cfi

otsikko "x86-64: CET-merkinnät"
# @alku cet
"$CC" -O2 -fcf-protection=full -S -o - laske.c |
    grep -E '^\s+(endbr64|call|ret)' | sed -E 's/\s+/ /g'
"$CC" -O2 -fcf-protection=full -c laske.c -o laske.o
readelf -n laske.o | grep -o 'x86 feature: .*'
# @loppu cet

otsikko "AArch64: PAC ja BTI"
# @alku pac
aarch64-linux-gnu-gcc -O2 -mbranch-protection=standard -S -o - laske.c |
    grep -E '^\s+(hint|blr|ret|bti)' | sed -E 's/\s+/ /g'
# @loppu pac
