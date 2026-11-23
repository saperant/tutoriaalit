#!/usr/bin/env bash
# Varmuuskopiointityökalun komentorivi: lyhyet valitsimet getoptsilla,
# oletusarvot, validointi ja käyttöohje. Työ itse on tässä vain
# tulostus, jotta esimerkki pysyy lyhyenä.
set -euo pipefail

# @alku kaytto
readonly OHJELMA=${0##*/}

kaytto() {
    cat <<OHJE
Käyttö: $OHJELMA [-v] [-n] [-k MÄÄRÄ] [-o HAKEMISTO] LÄHDE...
  -k MÄÄRÄ      säilytettävien varmuuskopioiden määrä (oletus 7)
  -o HAKEMISTO  kohdehakemisto (oletus ./varmuuskopiot)
  -n            kuivaharjoitus: näytä mitä tehtäisiin
  -v            monisanainen tuloste (voi toistaa)
  -h            tämä ohje
OHJE
}

kuole() {
    printf '%s: %s\n' "$OHJELMA" "$1" >&2
    exit "${2:-1}"
}
# @loppu kaytto

# @alku jasennys
sailyta=7
kohde=./varmuuskopiot
kuiva=0
puhelias=0

while getopts ':k:o:nvh' valitsin; do
    case $valitsin in
        k) sailyta=$OPTARG ;;
        o) kohde=$OPTARG ;;
        n) kuiva=1 ;;
        v) (( ++puhelias )) ;;
        h) kaytto; exit 0 ;;
        :) kuole "valitsin -$OPTARG vaatii arvon" 2 ;;
        ?) kuole "tuntematon valitsin -$OPTARG" 2 ;;
    esac
done
shift $(( OPTIND - 1 ))
# @loppu jasennys

# @alku validointi
[[ $sailyta =~ ^[1-9][0-9]*$ ]] ||
    kuole "-k: odotettiin positiivista kokonaislukua: $sailyta" 2
(( $# > 0 )) || { kaytto >&2; exit 2; }
# @loppu validointi

printf 'säilytä %d, kohde %s, kuiva %d, puhelias %d\n' \
    "$sailyta" "$kohde" "$kuiva" "$puhelias"
printf 'lähde: %s\n' "$@"
