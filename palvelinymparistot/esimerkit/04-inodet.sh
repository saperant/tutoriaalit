#!/usr/bin/env bash
# Tiedostojärjestelmä voi täyttyä kahdella tavalla: lohkot tai inodet
# loppuvat. ext4 päättää inodien määrän luontihetkellä. Esimerkki luo
# levykuvan tiedostoon ja kirjoittaa siihen debugfs-työkalulla, joten
# liittämistä (mount) eikä pääkäyttäjän oikeuksia tarvita.
set -euo pipefail
export LC_ALL=C
tyo=$(mktemp -d)
trap 'rm -rf "$tyo"' EXIT
kuva=$tyo/levy.img

# @alku luonti
# 4 MiB, 1 KiB:n lohkot ja vain 32 inodea (oletus olisi noin 1024).
mkfs.ext4 -q -F -b 1024 -N 32 -U clear -E root_owner=0:0 \
    "$kuva" 4M > /dev/null
# @loppu luonti

tila() {
    dumpe2fs -h "$kuva" 2>/dev/null \
        | grep -E '^(Inode count|Free inodes|Block count|Free blocks):' \
        | tr -s ' '
}

# @alku taytto
tila
for i in $(seq 1 40); do
    if ! debugfs -w -R "write /dev/null pieni-$i" "$kuva" 2>&1 \
            | grep -q 'Could not allocate inode'; then
        continue
    fi
    echo "tiedosto $i: inodet loppuivat"
    break
done
tila
# @loppu taytto
