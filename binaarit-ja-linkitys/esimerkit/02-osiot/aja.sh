#!/usr/bin/env bash
# Mihin osioon mikin muuttuja ja funktio päätyy.
source ./yhteinen.sh

"$CC" "${CFLAGS[@]}" -c main.c -o main.o
"$CC" main.o -o osiot
./osiot

otsikko "symbolit ja osiot (main.o)"
# @alku symbolit
# objdump -t: symbolitaulu, jossa näkyy kunkin symbolin osio.
nimet=" kuukausien_paivat laskuri puskuri kutsuja valimuisti
       paivia_vuodessa main "
objdump -t main.o | awk -v nimet="$nimet" '
    { nimi = $NF; sub(/\.[0-9]+$/, "", nimi) }  # valimuisti.0 -> valimuisti
    index(nimet, " " nimi) && nimi != "" { print nimi, $(NF - 2) }' | sort
# @loppu symbolit

otsikko "osiot (main.o)"
# @alku osiot
# Osion nimi ja tyyppi: NOBITS ei vie tilaa tiedostossa.
readelf -S -W main.o | sed -E 's/^ *\[ *[0-9]+\] //' |
    awk '$1 ~ /^\.(text|data|bss|rodata)/ { print $1, $2 }'
# @loppu osiot

otsikko "segmentit (osiot)"
# @alku segmentit
# LOAD-segmentit, niiden oikeudet ja osiot, jotka kuhunkin kuuluvat.
readelf -l -W osiot | awk '
    /^  [A-Z_]+ +0x/ {
        if ($1 == "LOAD") {
            oik = $7; for (i = 8; i < NF; i++) oik = oik $i
            load[nro] = oik
        }
        nro++
    }
    /^   [0-9][0-9] / && ($1 + 0) in load {
        rivi = ""
        for (i = 2; i <= NF; i++)
            if ($i ~ /^\.(text|rodata|data|bss)$/) rivi = rivi " " $i
        print "LOAD", load[$1 + 0] ":" rivi
    }'
# @loppu segmentit
