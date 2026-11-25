#!/usr/bin/env bash
# Virheenjäljitystieto: DWARF, osoitteesta riviksi ja erillinen
# debug-tiedosto.
source ./yhteinen.sh

otsikko "käännös virheenjäljitystiedon kanssa"
# @alku kaanto
"$CC" "${CFLAGS[@]}" -g -o jono jono.c
readelf -S -W jono | grep -oE '\.debug_[a-z_]+' | sort |
    paste -sd ' ' | fmt -w 72
# Omassa tiedostossa (decl_file 1) esitellyt funktiot ja niiden rivit.
readelf --debug-dump=info jono | awk '
    /DW_TAG/            { aliohjelma = /DW_TAG_subprogram/; nimi = "" }
    aliohjelma && /DW_AT_name/      { nimi = $NF }
    aliohjelma && /DW_AT_decl_file/ { oma = ($NF == 1) }
    aliohjelma && oma && nimi != "" && /DW_AT_decl_line/ {
        print "funktio", nimi, "rivillä", $NF }'
# @loppu kaanto

otsikko "kaatuminen ja osoitteesta riviksi"
# @alku kaatuminen
./jono
{ ./jono tyhja && exit 1; echo "paluuarvo $? (SIGSEGV = 11, 128 + 11)"; } \
    2> /dev/null
funktio=$(nm jono | awk '$3 ~ /^viimeinen/ { print $1 }')
addr2line -f -e jono "0x$funktio" | sed -E 's|^.*/||; s/ \(discr.*//'
# @loppu kaatuminen

otsikko "erillinen debug-tiedosto"
# @alku erillinen
objcopy --only-keep-debug jono jono.debug
strip --strip-debug --strip-unneeded jono -o jono.riisuttu
objcopy --add-gnu-debuglink=jono.debug jono.riisuttu
for t in jono jono.riisuttu jono.debug; do
    printf '%-14s debug-osioita %s\n' "$t" \
        "$(readelf -S -W "$t" 2> /dev/null | grep -c ' \.debug_')"
done
readelf --string-dump=.gnu_debuglink jono.riisuttu | grep -oE 'jono\.debug'
addr2line -f -e jono.debug "0x$funktio" | sed -E 's|^.*/||'
# @loppu erillinen
