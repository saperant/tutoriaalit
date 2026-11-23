#!/usr/bin/env bash
# Pitkät valitsimet (--kohde=X, --kohde X) jäsennetään käsin
# while-case-silmukalla. getopts ei tue niitä, ja ulkoisen getopt(1)-
# ohjelman pitkät valitsimet ovat GNU-laajennus.
set -euo pipefail

kuole() { printf '%s\n' "$1" >&2; exit 2; }

# @alku silmukka
kohde=./julkaisu
ymparisto=
kuiva=0
lahteet=()

while (( $# > 0 )); do
    case $1 in
        --kohde=*)    kohde=${1#*=} ;;
        --kohde)      (( $# > 1 )) || kuole "--kohde vaatii arvon"
                      kohde=$2; shift ;;
        --ymparisto=*) ymparisto=${1#*=} ;;
        -n|--kuiva)   kuiva=1 ;;
        --)           shift; lahteet+=("$@"); break ;;
        -*)           kuole "tuntematon valitsin: $1" ;;
        *)            lahteet+=("$1") ;;
    esac
    shift
done
# @loppu silmukka

# @alku validointi
case $ymparisto in
    testi|tuotanto) ;;
    '') kuole "--ymparisto on pakollinen" ;;
    *)  kuole "tuntematon ympäristö: $ymparisto" ;;
esac
# @loppu validointi

printf 'kohde=%s ympäristö=%s kuiva=%d\n' "$kohde" "$ymparisto" "$kuiva"
printf 'lähde: %s\n' "${lahteet[@]}"
