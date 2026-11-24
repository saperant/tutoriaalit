# shellcheck shell=bash
# Esimerkkien yhteiset asetukset. Jokainen aja.sh lukee tämän.
set -euo pipefail
export LC_ALL=C
CC=$(command -v gcc-14 || command -v gcc)
CXX=$(command -v g++-14 || command -v g++)
# shellcheck disable=SC2034  # käytetään aja.sh-skripteissä
CFLAGS=(-std=c17 -O2 -Wall -Wextra -Werror)
export CC CXX

# otsikko TEKSTI: tulosteen väliotsikko
otsikko() { printf '== %s\n' "$*"; }

# symbolit TIEDOSTO NIMI...: symbolin tyyppikirjain (nm) nimen mukaan
symbolit() {
    local tiedosto=$1
    shift
    nm "$tiedosto" | awk -v nimet=" $* " '
        { n = $NF; t = $(NF - 1) }
        index(nimet, " " n " ") { print t, n }' | sort -k2
}

# virherivi KOMENTO...: ajaa komennon, jonka odotetaan epäonnistuvan,
# ja tulostaa linkkerin virheilmoituksen ilman tiedostopolkuja ja
# osoitteita
virherivi() {
    if "$@" > virhe.txt 2>&1; then
        echo "odotettiin virhettä, mutta komento onnistui"
        return 1
    fi
    grep -oE "(undefined reference to|multiple definition of) \`[^']+'" \
        virhe.txt | sort -u
}
