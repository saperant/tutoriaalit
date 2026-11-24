#!/usr/bin/env bash
# Ensimmäinen virtuaalikone: oma pieni käyttöjärjestelmän ydin ajetaan
# QEMU:lla. Ohjelma käännetään vieraaksi ja käynnistetään ilman levyä.
set -euo pipefail
hak=$(dirname "$0")
tyo=$(mktemp -d)
trap 'rm -rf "$tyo"' EXIT

"$hak/vieras/lahteet/rakenna.sh" "$hak/vieras/lahteet/hei.c" "$tyo/hei.elf"

# @alku qemu
# -accel tcg: käskyt käännetään ohjelmallisesti (toimii ilman KVM:ää)
# -serial stdio: vieraan sarjaportti näkyy päätteessä
# isa-debug-exit: vieras voi sammuttaa koneen ja antaa paluuarvon
tila=0
qemu-system-x86_64 -machine pc -accel tcg -m 16M \
    -display none -monitor none -no-reboot \
    -serial stdio \
    -device isa-debug-exit,iobase=0xf4,iosize=0x04 \
    -kernel "$tyo/hei.elf" || tila=$?
echo "QEMU päättyi, paluuarvo $tila = ($(( tila >> 1 )) << 1) | 1"
# @loppu qemu
