#!/usr/bin/env bash
# Koko laitteen emulointi QEMU:ssa: komentosarja, binäärisen tulosteen
# tallennus, toistettavuus ja käynnistyslataimen tarkistus.
source ./yhteinen.sh
vedos=$LAITE/flash.bin

# @alku istunto
kaiku=$(python3 kehys.py 5 "$(printf 'hei' | od -An -tx1 | tr -d ' ')")
{
    echo "aja 2400"
    echo "tila"
    echo "kehys $kaiku"
    echo "siirra"
    echo "sammuta"
} > syote.txt
qemu_raw "$vedos" < syote.txt > istunto.bin
# @loppu istunto
otsikko "istunnon tekstiosat"
# @alku teksti
strings -n 5 istunto.bin
# @loppu teksti
otsikko "kehykset heksana"
# @alku kehykset
alku=$(grep -abo $'\x7e\x05' istunto.bin | head -1 | cut -d: -f1)
python3 heksa.py istunto.bin "$alku" 64
# @loppu kehykset
otsikko "toistettavuus"
# @alku toisto
qemu_raw "$vedos" < syote.txt > toinen.bin
cmp istunto.bin toinen.bin && echo "kaksi ajoa: tavulleen samat"
# @loppu toisto
otsikko "muutettu sovellus: yksi tavu flashissa"
# @alku muutos
cp "$vedos" muutettu.bin
printf '\x00' | dd of=muutettu.bin bs=1 seek=$((0x10400)) conv=notrunc \
    status=none
printf 'sammuta\n' | qemu muutettu.bin
# @loppu muutos
