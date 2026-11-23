#!/usr/bin/env bash
# Julkaisu versioituihin hakemistoihin ja atominen vaihto
# symbolisella linkillä. Palvelu lukee aina hakemistoa nykyinen/, joka
# osoittaa joko vanhaan tai uuteen versioon, ei koskaan puolivalmiiseen.
set -euo pipefail
export LC_ALL=C

# @alku vaihto
JULKAISUT=julkaisut
SAILYTA=2

julkaise() {
    local versio=$1 kohde="$JULKAISUT/$1"
    [[ ! -e $kohde ]] || { echo "versio $versio on jo olemassa" >&2
                           return 1; }
    mkdir -p "$kohde.kesken"
    printf 'versio=%s\n' "$versio" > "$kohde.kesken/sovellus.conf"
    mv -T -- "$kohde.kesken" "$kohde"

    ln -sfn -- "$versio" "$JULKAISUT/nykyinen.uusi"
    mv -T -- "$JULKAISUT/nykyinen.uusi" "$JULKAISUT/nykyinen"
}
# @loppu vaihto

# @alku siivous
siivoa_vanhat() {
    local -a versiot
    mapfile -t versiot < <(find "$JULKAISUT" -mindepth 1 -maxdepth 1 \
        -type d -name 'v*' -printf '%f\n' | sort -V)
    local poistettavia=$(( ${#versiot[@]} - SAILYTA ))
    (( poistettavia > 0 )) || return 0
    local versio
    for versio in "${versiot[@]:0:poistettavia}"; do
        rm -rf -- "${JULKAISUT:?}/$versio"
    done
}
# @loppu siivous

# @alku yritys
yrita() {                       # yrita KERTAA KOMENTO...
    local kertaa=$1 kerta viive=1; shift
    for (( kerta = 1; ; kerta++ )); do
        "$@" && return 0
        (( kerta < kertaa )) || return 1
        echo "yritys $kerta epäonnistui, uusi yritys" >&2
        sleep "0.0$viive"       # esimerkissä lyhyt; oikeasti sekunteja
        (( viive *= 2 ))
    done
}
# @loppu yritys

# @alku ajo
for versio in v1.9.0 v1.10.0 v1.10.1; do
    yrita 3 julkaise "$versio"
    siivoa_vanhat
done
julkaise v1.10.1 2> /dev/null || echo "uudelleenjulkaisu estettiin"
ls "$JULKAISUT"
cat "$JULKAISUT/nykyinen/sovellus.conf"
# @loppu ajo
