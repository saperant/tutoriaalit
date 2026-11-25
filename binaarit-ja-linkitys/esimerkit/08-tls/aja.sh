#!/usr/bin/env bash
# Säiekohtainen muisti (TLS): osiot, PT_TLS ja kolme tapaa osoittaa
# säikeen muuttujaa.
source ./yhteinen.sh

# relokaatiot OBJEKTI: funktion kasvata TLS-relokaatiot
relokaatiot() {
    readelf -r -W "$1" | awk '/TLS|TPOFF|tls_get_addr/ { print $3, $5 }' |
        sed -E 's/[-+]0?x?[0-9a-f]+$//' | sort -u
}

otsikko "osiot ja segmentti"
# @alku osiot
"$CC" "${CFLAGS[@]}" -c laskuri.c -o laskuri.o
readelf -S -W laskuri.o | sed -E 's/^ *\[ *[0-9]+\] //' |
    awk '$1 ~ /^\.t(data|bss)$/ { print $1, $2, "liput", $7 }'
"$CC" "${CFLAGS[@]}" main.c laskuri.o -o tls
readelf -l -W tls |
    awk '$1 == "TLS" { print "TLS FileSiz", $5, "MemSiz", $6 }'
# @loppu osiot

otsikko "ohjelmassa: siirtymä säikeen osoittimesta (local-exec)"
# @alku ohjelma
relokaatiot laskuri.o
objdump -d --no-show-raw-insn --no-addresses laskuri.o |
    sed -n '/<kasvata>:/,$p' | expand -t 4
# @loppu ohjelma

otsikko "jaetussa kirjastossa: funktiokutsu (general-dynamic)"
# @alku kirjasto
"$CC" "${CFLAGS[@]}" -fPIC -c laskuri.c -o pic.o
relokaatiot pic.o
# @loppu kirjasto

otsikko "kirjastossa, joka ladataan käynnistyksessä (initial-exec)"
# @alku initial
"$CC" "${CFLAGS[@]}" -fPIC -ftls-model=initial-exec -c laskuri.c -o ie.o
relokaatiot ie.o
# @loppu initial

otsikko "ajo"
./tls
