#!/usr/bin/env bash
# Funktion tulos välitetään tulosteena, onnistuminen paluuarvona ja
# taulukko nimiviittauksella.
set -euo pipefail

# @alku tuloste
# Palauttaa levyosion käyttöasteen prosentteina. Paluuarvo 1, jos
# osiota ei löydy.
kayttoaste() {
    local osio=$1 rivi
    while read -r rivi; do
        local kentat
        read -ra kentat <<< "$rivi"
        if [[ ${kentat[5]} == "$osio" ]]; then
            echo "${kentat[4]%\%}"
            return 0
        fi
    done < <(printf '%s\n' \
        "/dev/sda1 50G 41G 9G 82% /" \
        "/dev/sdb1 200G 20G 180G 10% /data")
    return 1
}
# @loppu tuloste

# @alku kaytto
if aste=$(kayttoaste /); then
    echo "juuriosio: $aste %"
fi
if ! kayttoaste /backup > /dev/null; then
    echo "osiota /backup ei löytynyt"
fi
# @loppu kaytto

# @alku nimiviittaus
# Lisää taulukkoon vain uudet alkiot. Taulukon nimi annetaan
# argumenttina, ja declare -n tekee siitä viittauksen.
lisaa_uniikki() {
    local -n kohde=$1
    local alkio=$2 olemassa
    for olemassa in "${kohde[@]}"; do
        [[ $olemassa == "$alkio" ]] && return 0
    done
    kohde+=("$alkio")
}

palvelut=()
for p in api jono api loki jono; do
    lisaa_uniikki palvelut "$p"
done
echo "palvelut: ${palvelut[*]}"
# @loppu nimiviittaus

# @alku local
laskuri=0
kasvata() {
    local laskuri=100       # varjostaa globaalin muuttujan
    laskuri=$((laskuri + 1))
    echo "funktiossa: $laskuri"
}
kasvata
echo "globaali: $laskuri"
# @loppu local
