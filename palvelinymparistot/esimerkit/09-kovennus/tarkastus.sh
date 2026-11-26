#!/usr/bin/env bash
# Tarkistusfunktioita kutsutaan saanto-funktion kautta:
# shellcheck disable=SC2317
# CIS-tyylinen koventamisen tarkastus: jokainen sääntö tarkistaa yhden
# asian ja tulostaa PASS tai FAIL. Juurihakemisto annetaan
# argumenttina (oikealla palvelimella /), joten tarkastusta voi testata
# ja ajaa myös levykuvalle tai kontin tiedostojärjestelmälle.
set -euo pipefail
export LC_ALL=C

# @alku saannot
juuri=${1:-}
tulos=0
saanto() {  # saanto <tunniste> <kuvaus> <komento...>
    local tunniste=$1 kuvaus=$2
    shift 2
    if "$@"; then
        printf 'PASS %-6s %s\n' "$tunniste" "$kuvaus"
    else
        printf 'FAIL %-6s %s\n' "$tunniste" "$kuvaus"
        tulos=1
    fi
}
sshd_arvo() {  # sshd_arvo <avain> <odotettu>
    local arvo
    arvo=$(awk -v k="$1" 'tolower($1) == tolower(k) { print $2; exit }' \
        "$juuri/etc/ssh/sshd_config")
    [[ ${arvo,,} == "${2,,}" ]]
}
oikeudet_enintaan() {  # oikeudet_enintaan <tiedosto> <oktaali>
    local nyt
    nyt=$(stat -c '%a' "$juuri$1")
    (( (8#$nyt & ~8#$2) == 0 ))
}
ei_kaikkien_kirjoitettavia() {
    [[ -z $(find "$juuri/etc" -xdev -type f -perm -o+w -print -quit) ]]
}
# @loppu saannot

# @alku tarkastus
saanto SSH-1 "root ei kirjaudu SSH:lla" sshd_arvo PermitRootLogin no
saanto SSH-2 "salasanakirjautuminen pois" \
    sshd_arvo PasswordAuthentication no
saanto SSH-3 "enintään 4 yritystä" \
    sh -c "awk '/^MaxAuthTries/ { exit !(\$2 <= 4) }' \
        '$juuri/etc/ssh/sshd_config'"
saanto FS-1  "/etc/shadow enintään 640" oikeudet_enintaan /etc/shadow 640
saanto FS-2  "/etc:ssä ei kaikkien kirjoitettavia" \
    ei_kaikkien_kirjoitettavia
saanto UPD-1 "automaattiset tietoturvapäivitykset" grep -q \
    'Unattended-Upgrade "1"' "$juuri/etc/apt/apt.conf.d/20auto-upgrades"
exit "$tulos"
# @loppu tarkastus
