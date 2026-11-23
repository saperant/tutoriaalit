#!/usr/bin/env bash
# sed: korvaukset, osoitteet ja muokkaus paikallaan.
set -euo pipefail
export LC_ALL=C

cat > palvelu.conf <<'ASETUKSET'
# Palvelun asetukset
portti = 8080

osoite = 0.0.0.0   # kuunnellaan kaikkia
# loki = /var/log/palvelu.log
loki = /tmp/palvelu.log
ASETUKSET

# @alku kommentit
sed -e 's/[[:space:]]*#.*//' -e '/^[[:space:]]*$/d' palvelu.conf
# @loppu kommentit

# @alku paikallaan
sed -i.bak 's/^portti = .*/portti = 9090/' palvelu.conf
diff palvelu.conf.bak palvelu.conf || true
# @loppu paikallaan

# @alku ryhmat
printf '%s\n' 'maksettu 02.11.2026' 'eräpäivä 30.1.2027' \
    | sed -E 's/([0-9]{1,2})\.([0-9]{1,2})\.([0-9]{4})/\3-\2-\1/'
# @loppu ryhmat

# @alku osoitteet
seq 1 10 | sed -n '3,5p'
seq 1 10 | sed '2~3d' | paste -sd' '
# @loppu osoitteet
