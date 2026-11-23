#!/usr/bin/env bash
# Pääohjelma lataa kirjastot omasta hakemistostaan riippumatta siitä,
# mistä skripti käynnistetään.
# shellcheck source-path=SCRIPTDIR
set -euo pipefail

# @alku lataus
HAKEMISTO=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source "$HAKEMISTO/loki.sh"
source "$HAKEMISTO/asetukset.sh"
# @loppu lataus

# @alku kaytto
LOKI_AIKA=12:00:00      # kiinteä aika, jotta tuloste on toistettava
exec 2>&1               # loki näkyviin tulosteen joukossa
cat > palvelu.conf <<'ASETUKSET'
# palvelun asetukset
PORTTI=8080
NIMI=laskutus $(rm -rf ~)
virheellinen rivi
ASETUKSET

declare -A asetukset=()
lue_asetukset palvelu.conf asetukset
loki info "portti ${asetukset[PORTTI]}"
printf 'NIMI = %s\n' "${asetukset[NIMI]}"
loki debug "ei näy oletustasolla"
# @loppu kaytto
