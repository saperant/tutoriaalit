#!/usr/bin/env bash
# Syötteen validointi [[ ]]-testeillä, säännöllisillä lausekkeilla ja
# case-rakenteella. Jokainen rivi on muotoa: nimi portti ympäristö.
set -euo pipefail

# @alku funktiot
on_kelvollinen_nimi() {
    [[ $1 =~ ^[a-z][a-z0-9-]{1,30}$ ]]
}

on_kelvollinen_portti() {
    [[ $1 =~ ^[0-9]+$ ]] && (( $1 >= 1 && $1 <= 65535 ))
}
# @loppu funktiot

# @alku case
ympariston_taso() {
    case $1 in
        prod | tuotanto) echo 3 ;;
        test* | qa)      echo 2 ;;
        dev | kehitys)   echo 1 ;;
        *)               return 1 ;;
    esac
}
# @loppu case

# @alku kaytto
while read -r nimi portti ymparisto; do
    if ! on_kelvollinen_nimi "$nimi"; then
        echo "hylätty: virheellinen nimi '$nimi'"
    elif ! on_kelvollinen_portti "$portti"; then
        echo "hylätty: $nimi: virheellinen portti '$portti'"
    elif ! taso=$(ympariston_taso "$ymparisto"); then
        echo "hylätty: $nimi: tuntematon ympäristö '$ymparisto'"
    else
        echo "ok: $nimi:$portti (taso $taso)"
    fi
done
# @loppu kaytto

# @alku rematch
versio='palvelin-2.14.3-rc1'
if [[ $versio =~ ([0-9]+)\.([0-9]+)\.([0-9]+) ]]; then
    echo "pää ${BASH_REMATCH[1]}, sivu ${BASH_REMATCH[2]}," \
         "korjaus ${BASH_REMATCH[3]}"
fi
# @loppu rematch
