# shellcheck shell=bash
# Esimerkkien yhteiset asetukset. Jokainen aja.sh lukee tämän.
set -euo pipefail
export LC_ALL=C
CC=$(command -v gcc-14 || command -v gcc)
CXX=$(command -v g++-14 || command -v g++)
export CC CXX

# otsikko TEKSTI: tulosteen väliotsikko
otsikko() { printf '== %s\n' "$*"; }

# normalisoi: poistaa purkutulosteesta osoitteet ja siirtymät, jotka
# vaihtelevat kääntäjän ja linkkerin version mukaan
normalisoi() {
    expand -t 8 |
        sed -E -e '/^$/d; /file format|^Disassembly of section/d' \
            -e '/^ +((data16 )*(cs )?nop|xchg +ax,ax)/d' \
            -e 's/^ +/    /; s/ +$//; s/  +/ /g; s/^ /    /' \
            -e 's/\b[0-9a-f]{3,} </</g' \
            -e 's/\[rip\+0x[0-9a-f]+\]/[rip+X]/g' \
            -e 's/# 0x[0-9a-f]+ /# /; s/# [0-9a-f]+ </# </'
}

# @alku purku
# purku TIEDOSTO FUNKTIO [VALITSIMET...]: funktion konekieli
# Intel-syntaksilla ilman osoitteita ja konekielen tavuja
purku() {
    local tiedosto=$1 funktio=$2
    shift 2
    objdump -d -M intel --no-show-raw-insn --no-addresses \
        --disassemble="$funktio" "$@" "$tiedosto" | normalisoi
}
# @loppu purku

# r2 TIEDOSTO KOMENNOT: radare2 eräajona ilman värejä. Osoitteet
# korvataan sanalla OSOITE, käskyjen vakiot säilyvät. Analyysin
# edistymisviestit menevät virhetulosteeseen.
r2() {
    command r2 -q -e scr.color=0 -e scr.utf8=false -e bin.cache=true \
        -e asm.bytes=false -e asm.offset=false -e scr.interactive=false \
        -c "$2" "$1" 2> /dev/null |
        sed -E -e 's/0x0000[0-9a-f]{4}\b/OSOITE/g' \
            -e 's/\b(j[a-z]+|call) 0x[0-9a-f]+/\1 OSOITE/g' \
            -e 's/(@|from) 0x[0-9a-f]+/\1 OSOITE/g' \
            -e 's/OSOITE, 0x[0-9a-f]+/OSOITE, OSOITE/g' \
            -e 's/^(\S+) 0x[0-9a-f]+ \[/\1 OSOITE [/' \
            -e 's/loc_0x[0-9a-f]+/loc_OSOITE/g' \
            -e 's/^0x[0-9a-f]+/OSOITE/; s/fcn\.[0-9a-f]{8}/fcn.OSOITE/g' \
            -e 's/^\[OSOITE\]> //' -e 's/ {3,};/  ;/' -e 's/ +$//'
}

# gdb_era SKRIPTI OHJELMA [ARGUMENTIT...]: gdb eräajona. Tulosteesta
# jätetään vain rivit, jotka alkavat merkillä '>' (skriptin omat).
gdb_era() {
    local skripti=$1
    shift
    gdb -q -batch -nx -ex 'set disable-randomization off' \
        -ex 'set debuginfod enabled off' -x "$skripti" --args "$@" \
        2>&1 | grep '^>' || true
}
