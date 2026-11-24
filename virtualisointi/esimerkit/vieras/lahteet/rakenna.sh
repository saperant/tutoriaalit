#!/usr/bin/env bash
# Kääntää vieraan C-tiedostosta Multiboot-ytimeksi.
# Käyttö: rakenna.sh lahde.c tulos.elf
set -euo pipefail
hak=$(dirname "$0")
cc=$(command -v gcc-14 || command -v gcc)
tyo=$(mktemp -d)
trap 'rm -rf "$tyo"' EXIT
"$cc" -m32 -ffreestanding -fno-pie -fno-stack-protector -O2 \
    -Wall -Wextra -Werror -c "$1" -o "$tyo/vieras.o"
"$cc" -m32 -c "$hak/alku.S" -o "$tyo/alku.o"
ld -m elf_i386 -T "$hak/linkki.ld" --no-warn-rwx-segments \
    -o "$2" "$tyo/alku.o" "$tyo/vieras.o"
