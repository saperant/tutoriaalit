#!/usr/bin/env bash
# Yksikkötiedostojen tarkistus ilman käynnissä olevaa systemd:tä:
# syntaksi ja viittaukset (verify), altistuksen arvio (security) ja
# ajastimen kalenterilauseke (calendar).
set -euo pipefail
export LC_ALL=C.UTF-8 TZ=UTC SYSTEMD_COLORS=0 SYSTEMD_PAGER=cat
cd "$(dirname "$0")/yksikot"
tyo=$(mktemp -d)
trap 'rm -rf "$tyo"' EXIT

# @alku tarkista
# tarkista YKSIKKÖ...: tulostaa näitä yksiköitä koskevat löydökset.
# verify lukee myös riippuvuudet, joten koneen muiden yksiköiden
# varoitukset rajataan pois.
tarkista() {
    local koodi=0
    systemd-analyze verify --man=no --recursive-errors=one "$@" \
        2> "$tyo/virheet" || koodi=$?
    sed 's#^/.*/##' "$tyo/virheet" |
        grep -E '^(mittari|raportti|rikki)\.' || true
    echo "paluuarvo $koodi"
}
echo "== kunnossa olevat yksiköt"
tarkista mittari.service mittari.socket raportti.service raportti.timer
echo "== viallinen yksikkö"
tarkista rikki.service
# @loppu tarkista

# @alku altistus
# altistus YKSIKKÖ: arvio 0 (suojattu) – 10 (altis) ja sanallinen luokka
altistus() {
    systemd-analyze security --offline=true --no-pager "$1" 2> /dev/null |
        awk '/Overall exposure level/ { print $(NF - 2), $(NF - 1) }'
}
echo "== altistus kovennus kerrallaan"
cp mittari.service mittari.socket "$tyo"/
mkdir "$tyo/mittari.service.d"
printf '%-20s %s\n' "ilman kovennusta" "$(altistus "$tyo/mittari.service")"
for lisays in mittari.service.d/*.conf; do
    cp "$lisays" "$tyo/mittari.service.d/"
    printf '+ %-18s %s\n' "$(basename "$lisays")" \
        "$(altistus "$tyo/mittari.service")"
done
# @loppu altistus

# @alku jaljella
echo "== mitä arvio vielä huomauttaa (paino ja asetus)"
systemd-analyze security --offline=true --no-pager --json=short \
    mittari.service 2> /dev/null | python3 -c '
import json, sys
for kohta in json.load(sys.stdin):
    if not kohta["set"]:
        print(kohta["exposure"], kohta["name"])'
# @loppu jaljella

# @alku kynnys
echo "== kynnysarvo putkessa: altistus enintään 2.0"
for yksikko in "$tyo/mittari.service" raportti.service; do
    if systemd-analyze security --offline=true --threshold=20 \
            --no-pager "$yksikko" > /dev/null 2>&1; then
        echo "$(basename "$yksikko"): hyväksytty"
    else
        echo "$(basename "$yksikko"): hylätty ($(altistus "$yksikko"))"
    fi
done
# @loppu kynnys

# @alku ajastin
echo "== ajastimen seuraavat ajot keskiviikosta 25.11.2026 klo 12"
lauseke=$(sed -n 's/^OnCalendar=//p' raportti.timer)
systemd-analyze calendar --iterations=3 \
    --base-time='2026-11-25 12:00:00 UTC' "$lauseke" |
    grep -E 'Normalized|Next|Iteration' | sed 's/^ *//'
# @loppu ajastin
