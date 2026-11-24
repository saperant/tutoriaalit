#!/usr/bin/env bash
# C++-ohjelman takaisinmallinnus: nimet, virtuaalitaulut, RTTI,
# poikkeukset ja kirjaston tyyppien muistiasettelu.
source ./yhteinen.sh

"$CXX" -std=c++23 -O1 -Wall -Wextra -Werror muodot.cpp -o muodot
./muodot
otsikko "koristellut nimet ja niiden purku"
# @alku nimet
nm --defined-only muodot | awk '{ print $3 }' |
    grep -E '^_Z(N11SuorakulmioD|NK6Ympyra9|3luo|TS6)' | sort |
    while read -r nimi; do
        echo "$nimi"
        c++filt "$nimi" | fold -s -w 70 | sed 's/^/    /; s/ *$//'
    done
# @loppu nimet
# @loppu nimet
otsikko "virtuaalitaulut ja RTTI"
# @alku vtaulu
python3 vtaulu.py muodot Ympyra Suorakulmio Muoto
# @loppu vtaulu
otsikko "virtuaalikutsu"
# @alku virtuaalikutsu
kokonaisala=$(nm muodot | awk '$3 ~ /kokonaisala/ { print $3 }')
purku muodot "$kokonaisala" | sed -n '/QWORD PTR \[rbx\]/,/call/p'
# @loppu virtuaalikutsu
# @loppu virtuaalikutsu
otsikko "poikkeukset ja tyyppitarkistus"
# @alku poikkeukset
readelf -SW muodot | grep -oE '\.(eh_frame(_hdr)?|gcc_except_table)' | sort
objdump -d -C --no-show-raw-insn muodot | awk '
    /^[0-9a-f]+ <.*>:$/ {
        funktio = substr($0, index($0, "<") + 1); sub(/[(>].*/, "", funktio) }
    /call.*<(__cxa_throw|__cxa_begin_catch|__dynamic_cast)@plt>/ {
        sub(/.*</, "", $NF); print funktio, "kutsuu", $NF }' |
    sed 's/@plt>$//' | sort -u
# @loppu poikkeukset
otsikko "std::string ja std::vector muistissa (gdb)"
"$CXX" -std=c++23 -O0 -g -Wall -Wextra -Werror muodot.cpp -o muodot-g
gdb_era asettelu.gdb ./muodot-g
