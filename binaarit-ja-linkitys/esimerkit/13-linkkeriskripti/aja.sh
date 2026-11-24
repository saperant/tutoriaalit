#!/usr/bin/env bash
# Linkkeriskriptit: lisäys oletusskriptiin ja kokonainen oma skripti.
source ./yhteinen.sh

otsikko "lisäys oletusskriptiin"
# @alku anturi
"$CC" "${CFLAGS[@]}" anturi.c -o anturi -Wl,-T,kalibrointi.ld
./anturi
nm anturi | awk '$3 == "KALIBROINTI_VERSIO" { print $2, $3, "=", $1 + 0 }
                $3 == "korjaus" { print $2, $3 }'
readelf -S -W anturi | sed -E 's/^ *\[ *[0-9]+\] //' |
    awk '{ print $1 }' | grep -A1 -E '^\.rodata$'
# @loppu anturi

otsikko "oma skripti, ei C-kirjastoa"
# @alku irrallinen
"$CC" -O2 -ffreestanding -fno-pie -no-pie -nostdlib -static \
    -fno-stack-protector -fcf-protection=none -Wall -Wextra -Werror \
    irrallinen.c -o irrallinen -Wl,-T,irrallinen.ld,--build-id=none
./irrallinen
readelf -h irrallinen | grep -oE 'Entry point address: +0x[0-9a-f]+' |
    tr -s ' '
nm irrallinen | grep -E ' _start$'
readelf -S -W irrallinen | sed -E 's/^ *\[ *[0-9]+\] //' |
    awk '$1 ~ /^\.(text|rodata)$/ { print $1, $3 }'
# @loppu irrallinen
