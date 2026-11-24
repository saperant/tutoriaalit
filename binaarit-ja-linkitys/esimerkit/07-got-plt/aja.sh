#!/usr/bin/env bash
# Sijainnista riippumaton koodi, GOT ja PLT sekä laiska sidonta.
source ./yhteinen.sh

otsikko "relokaatiot -fPIC-objektissa"
# @alku pic
"$CC" "${CFLAGS[@]}" -fPIC -c mittari.c -o mittari.o
readelf -r -W mittari.o |
    awk '/^[0-9a-f]+ / && $5 ~ /^(kutsuja|pyorista)/ { print $3, $5 }'
# @loppu pic

otsikko "mittaa kirjastossa"
mittaa_konekieli() {
    objdump -d --no-show-raw-insn --no-addresses "$1" |
        sed -n '/<mittaa>:/,/^$/p' | sed '/^$/d' | expand -t 4 |
        sed -E 's/0x[1-9a-f][0-9a-f]*\(%rip\)/SIIRTYMA(%rip)/; s/ +# / # /
                s/# <[a-z_]+-0x[0-9a-f]+>/# <GOT-paikka>/'
}
# @alku nakyvyys
"$CC" -shared mittari.o -o libmittari.so
mittaa_konekieli libmittari.so
"$CC" "${CFLAGS[@]}" -fPIC -fvisibility=hidden -c mittari.c -o piilo.o
"$CC" -shared piilo.o -o libpiilo.so
mittaa_konekieli libpiilo.so
# @loppu nakyvyys

"$CC" "${CFLAGS[@]}" -c main.c -o main.o

sidonnat() {
    LD_DEBUG=bindings LD_LIBRARY_PATH=. ./"$1" 2> sidonta.txt > /dev/null
    grep -oE "^(ennen|ensimmäisen).*|symbol \`mittaa'" sidonta.txt
}
liput() { readelf -d "$1" | grep -oE 'FLAGS(_1)?\).*' | tr -s ' '; }

otsikko "oletus: sidonta käynnistyksessä"
# @alku oletus
"$CC" main.o -L. -lmittari -o oletus
liput oletus
sidonnat oletus
# @loppu oletus

otsikko "laiska sidonta (-z lazy)"
# @alku laiska
"$CC" main.o -L. -lmittari -o laiska -Wl,-z,lazy
liput laiska
sidonnat laiska
# @loppu laiska
