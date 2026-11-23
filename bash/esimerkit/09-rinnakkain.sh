#!/usr/bin/env bash
# Rinnakkaiset taustatyöt rajoitetulla määrällä: enintään RAJA työtä
# kerrallaan, jokaisen työn tila kerätään ja epäonnistumiset
# raportoidaan lopuksi. Työ on tässä simuloitu sleep-komennolla.
set -euo pipefail

# @alku tyo
tarkista_palvelin() {
    local nimi=$1
    sleep "0.$(( RANDOM % 3 + 1 ))"
    [[ $nimi != *-vanha ]]          # vanhat palvelimet "epäonnistuvat"
}
# @loppu tyo

# @alku ajo
RAJA=3
declare -A tyot=()                  # PID -> palvelin
epaonnistuneet=()

odota_yksi() {
    local pid tila=0
    wait -n -p pid || tila=$?
    (( tila == 0 )) || epaonnistuneet+=("${tyot[$pid]}")
    unset 'tyot[$pid]'
}

for palvelin in web1 web2 db1-vanha db2 jono1 jono2-vanha valvonta; do
    (( ${#tyot[@]} < RAJA )) || odota_yksi
    tarkista_palvelin "$palvelin" &
    tyot[$!]=$palvelin
done
while (( ${#tyot[@]} > 0 )); do
    odota_yksi
done
# @loppu ajo

# @alku raportti
if (( ${#epaonnistuneet[@]} > 0 )); then
    # Valmistumisjärjestys vaihtelee, joten raportti lajitellaan.
    printf 'epäonnistui: %s\n' "${epaonnistuneet[@]}" | sort
    # Oikea skripti päättyisi tässä paluuarvoon 1.
fi
# @loppu raportti
