# shellcheck shell=bash
# Muuttujia käytetään esimerkkien skripteissä, jotka lukevat tämän.
# shellcheck disable=SC2034
# Esimerkkien yhteiset asetukset. Jokainen aja.sh lukee tämän.
set -euo pipefail
export LC_ALL=C
CC=$(command -v gcc-14 || command -v gcc)
CLANG=$(command -v clang-20 || command -v clang)
export CC CLANG
# LeakSanitizer ei toimi kaikissa konteissa (ptrace), ja vuodot ovat
# omien esimerkkiensä aihe; muut ASanin tarkistukset ovat päällä.
export ASAN_OPTIONS=detect_leaks=0:abort_on_error=0
export UBSAN_OPTIONS=print_stacktrace=0

# @alku liput
# Kääntäjän liput: varoitukset virheinä ja virheenjäljitystiedot.
VAROITUKSET=(-std=c23 -Wall -Wextra -Wformat=2 -Werror -g)
SANITOIJAT=("-fsanitize=address,undefined" -fno-sanitize-recover=all
            -fno-omit-frame-pointer)
# @loppu liput

# otsikko TEKSTI: tulosteen väliotsikko
otsikko() { printf '== %s\n' "$*"; }

# tila KOODI: paluuarvo luettavassa muodossa
tila() {
    case $1 in
        0) echo "paluuarvo 0" ;;
        132) echo "paluuarvo 132 (SIGILL)" ;;
        134) echo "paluuarvo 134 (SIGABRT)" ;;
        139) echo "paluuarvo 139 (SIGSEGV)" ;;
        *) echo "paluuarvo $1" ;;
    esac
}

# @alku kaatuu
# kaatuu KOMENTO...: ajaa komennon, jonka odotetaan päättyvän virheeseen,
# ja tulostaa paluuarvon sekä tiivistetyn virheraportin.
kaatuu() {
    local koodi=0
    # Ryhmän uudelleenohjaus vaientaa bashin oman signaali-ilmoituksen,
    # jossa on prosessinumero.
    { "$@" > ajo.out 2> ajo.err; } 2> /dev/null || koodi=$?
    if ((koodi == 0)); then
        echo "VIRHE: $1 ei kaatunut" >&2
        return 1
    fi
    tila "$koodi"
    python3 raportti.py < ajo.err
}
# @loppu kaatuu

# gdb_era SKRIPTI OHJELMA [ARGUMENTIT...]: gdb eräajona. Tulosteesta
# jätetään vain rivit, jotka alkavat merkillä '>' (skriptin omat).
gdb_era() {
    local skripti=$1
    shift
    gdb -q -batch -nx -ex 'set debuginfod enabled off' -x "$skripti" \
        --args "$@" 2>&1 | grep '^>' || true
}
