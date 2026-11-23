#!/usr/bin/env bash
# Jäljitys (xtrace) erilliseen tiedostoon: PS4 lisää jokaiseen riviin
# funktion ja rivinumeron, ja BASH_XTRACEFD pitää jäljen erillään
# ohjelman varsinaisesta tulosteesta.
set -euo pipefail

laske_alv() {
    local senttia=$1 prosentti=$2
    echo $(( (senttia * prosentti + 50) / 100 ))
}

# @alku jaljitys
exec {jalki}> jalki.txt
BASH_XTRACEFD=$jalki
PS4='+ ${FUNCNAME[0]:-main}:${LINENO}: '
set -x
alv=$(laske_alv 1999 24)
set +x
# @loppu jaljitys

echo "alv: $alv senttiä"
echo "--- jalki.txt"
cat jalki.txt
