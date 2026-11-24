#!/usr/bin/env bash
# Järjestelmä- ja kirjastokutsujen jäljitys sekä LD_PRELOAD-koukku.
source ./yhteinen.sh

"$CC" -std=c17 -O2 -Wall -Wextra -Werror kirjautuja.c -o kirjautuja
./kirjautuja arvaus || true
otsikko "strings: salasanaa ei näy"
strings kirjautuja | grep -ciE 'lumi' || true

otsikko "strace: tiedostot ja tulosteet"
# @alku strace
strace -o jalki.txt -e trace=openat,read,write,close \
    ./kirjautuja arvaus > /dev/null || true
sed -n '/asetukset.conf/,$p' jalki.txt | sed -E 's/ {2,}=/ =/'
# @loppu strace

otsikko "ltrace: kirjastokutsut"
# @alku ltrace
ltrace -e strcmp+fopen ./kirjautuja arvaus 2>&1 > /dev/null |
    sed -E 's/ +=.*$//'
# @loppu ltrace

otsikko "LD_PRELOAD-koukku"
# @alku preload
"$CC" -std=c17 -O2 -Wall -Wextra -Werror -fPIC -shared koukku.c \
    -o koukku.so
LD_PRELOAD=./koukku.so ./kirjautuja arvaus 2>&1 || true
./kirjautuja Lumi-2026
# @loppu preload
cat kirjautumiset.log
