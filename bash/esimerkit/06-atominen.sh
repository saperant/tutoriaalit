#!/usr/bin/env bash
# Tiedoston päivitys atomisesti: kirjoitetaan väliaikaistiedostoon samaan
# hakemistoon ja nimetään se kohteen päälle. Lukija näkee aina joko
# vanhan tai uuden version, ei koskaan puolikasta.
set -euo pipefail

# @alku funktio
# Käyttö: komento | kirjoita_atomisesti KOHDE
kirjoita_atomisesti() {
    local kohde=$1 tmp
    tmp=$(mktemp "$kohde.XXXXXX")
    if ! cat > "$tmp"; then
        rm -f -- "$tmp"
        return 1
    fi
    chmod 644 "$tmp"
    mv -f -- "$tmp" "$kohde"            # rename on atominen
}
# @loppu funktio

# @alku kaytto
printf 'versio=1\n' | kirjoita_atomisesti asetukset.ini
printf 'versio=2\nominaisuus=päällä\n' | kirjoita_atomisesti asetukset.ini
cat asetukset.ini
ls
# @loppu kaytto
