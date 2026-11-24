#!/usr/bin/env bash
# Kokonainen analyysi: riisutun vientityökalun tarkistealgoritmi
# selvitetään ja toteutetaan uudelleen yhteensopivuutta varten.
source ./yhteinen.sh

"$CC" -std=c23 -O2 -Wall -Wextra -Werror vienti.c -o vienti
strip -s vienti
otsikko "1. käyttäytyminen"
printf 'lampo 21.5\nkosteus 41\n' | ./vienti
otsikko "2. tuonnit"
nm -D vienti | awk '$1 == "U" { sub(/@.*/, "", $2); print $2 }' |
    paste -sd ' ' 
otsikko "3. main ja sen kutsuma funktio"
# @alku etsi
alku=$(readelf -h vienti | awk '/Entry point/ { print $4 }')
main=$(objdump -d -M intel --start-address="$alku" \
    --stop-address=$((alku + 38)) vienti |
    grep -oP 'lea +rdi,\[rip\+0x[0-9a-f]+\] +# \K[0-9a-f]+')
kutsu=$(command r2 -q -c "aaa; af @ 0x$main; pdf @ 0x$main" vienti \
    2> /dev/null | grep -oP 'call fcn\.\K[0-9a-f]+' | head -1)
r2 vienti "aaa; af @ 0x$main; afn main 0x$main; afn tarkiste 0x$kutsu;
    pdf @ main" | grep -E 'call' | sed 's/  ; [^;]*(.*$//'
# @loppu etsi
otsikko "4. tarkistefunktio"
# @alku pdf
r2 vienti "aaa; af @ 0x$main; afn main 0x$main; afn tarkiste 0x$kutsu;
    pdf @ tarkiste" |
    grep -v 'nop '
# @loppu pdf
otsikko "5. uudelleentoteutus ja eroavuustesti"
# @alku vertaa
python3 tarkiste.py laske "lampo 21.5" "kosteus 41"
python3 tarkiste.py vertaa ./vienti
# @loppu vertaa
