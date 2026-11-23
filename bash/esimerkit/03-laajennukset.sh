#!/usr/bin/env bash
# Parametrilaajennukset: polkujen ja merkkijonojen käsittely ilman
# ulkoisia komentoja.
set -euo pipefail

# @alku polut
polku='/var/log/nginx/access.log.2.gz'
echo "tiedosto:   ${polku##*/}"          # pisin etuliite */ pois
echo "hakemisto:  ${polku%/*}"           # lyhin jälkiliite /* pois
echo "ilman .gz:  ${polku%.gz}"
echo "pääte:      ${polku##*.}"
# @loppu polut

# @alku oletukset
echo "portti:     ${PORTTI:-8080}"       # oletus, jos tyhjä tai asettamaton
: "${YMPARISTO:=kehitys}"                # asettaa oletuksen muuttujaan
echo "ympäristö:  $YMPARISTO"
# @loppu oletukset

# @alku merkkijonot
nimi='tuotanto-palvelin-01'
echo "pituus:     ${#nimi}"
echo "isoilla:    ${nimi^^}"
echo "korvattu:   ${nimi//-/_}"
echo "osa:        ${nimi:9:8}"
# @loppu merkkijonot

# @alku pakollinen
tarkista() {
    local kohde=${1:?käyttö: tarkista KOHDE}
    echo "tarkistetaan $kohde"
}
tarkista tietokanta
# @loppu pakollinen
