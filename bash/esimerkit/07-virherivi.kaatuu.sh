#!/usr/bin/env bash
# ERR-ansa kertoo, millä rivillä ja missä komennossa virhe tapahtui,
# ennen kuin set -e lopettaa skriptin.
set -Eeuo pipefail

# @alku ansa
virhe() {
    local tila=$? rivi=$1 komento=$2
    printf 'virhe rivillä %d: %s (tila %d)\n' \
        "$rivi" "$komento" "$tila" >&2
}
trap 'virhe "$LINENO" "$BASH_COMMAND"' ERR
# @loppu ansa

# @alku virhe
lue_asetukset() {
    grep -q '^portti=' asetukset.conf
}
echo "käynnistetään" >&2
lue_asetukset
echo "tätä ei tulosteta"
# @loppu virhe
