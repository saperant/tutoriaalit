#!/usr/bin/env bash
# Komennon argumentit kootaan taulukkoon. Näin jokainen argumentti
# säilyy yhtenä sanana, vaikka siinä olisi välilyöntejä, ja valinnaiset
# argumentit voi lisätä ehdollisesti.
set -euo pipefail

# Näyttää komennon sellaisena kuin se ajettaisiin.
nayta() { printf '%q' "$1"; shift; printf ' %q' "$@"; printf '\n'; }

# @alku taulukko
varmuuskopioi() {
    local lahde=$1 kohde=$2 kuiva=${3:-ei}
    local -a komento=(rsync --archive --delete)
    if [[ $kuiva == kyllä ]]; then
        komento+=(--dry-run)
    fi
    local poisto
    for poisto in '*.tmp' 'cache/'; do
        komento+=(--exclude "$poisto")
    done
    komento+=("$lahde/" "$kohde/")
    nayta "${komento[@]}"
}

varmuuskopioi "/home/ada/Omat tiedostot" /mnt/varmuus kyllä
# @loppu taulukko
