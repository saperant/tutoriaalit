#!/usr/bin/env bash
# Ajaa yhden esimerkin: kopioi esimerkin hakemiston ja yhteiset lähteet
# (lahde/) tilapäishakemistoon, ajaa siellä esimerkin aja.sh:n ja
# vertaa tulosteen tiedostoon <esimerkki>.odotettu. Tilapäishakemiston
# polku korvataan tulosteessa sanalla TYO, jotta tuloste on sama joka
# koneella.
set -euo pipefail
nimi=${1%/}
juuri=$(cd "$(dirname "$0")" && pwd)
tyo=$(mktemp -d)
trap 'rm -rf "$tyo"' EXIT

cp -r "$juuri/lahde" "$tyo/lahde"
cp -r "$juuri/$nimi/." "$tyo/"
# Kaikki esimerkit käyttävät samaa kääntäjää, jotta tulosteet ovat samat.
export CC=gcc-14 LC_ALL=C DEBUGINFOD_URLS=
# Esimerkit ajavat omia make-komentojaan: ulomman makein asetukset
# (esim. -j ja jobserver) eivät saa vuotaa niihin.
unset MAKEFLAGS MFLAGS MAKELEVEL

tuloste=$( (cd "$tyo" && bash aja.sh) 2>&1 | sed "s|$tyo|TYO|g") || {
    echo "$nimi: aja.sh epäonnistui:" >&2
    echo "$tuloste" >&2
    exit 1
}
if [[ ${PAIVITA:-} == 1 ]]; then
    printf '%s\n' "$tuloste" > "$juuri/$nimi.odotettu"
    echo "päivitetty: $nimi.odotettu"
elif diff -u "$juuri/$nimi.odotettu" <(printf '%s\n' "$tuloste"); then
    echo "OK: $nimi"
else
    echo "$nimi: tuloste poikkeaa odotetusta" >&2
    exit 1
fi
