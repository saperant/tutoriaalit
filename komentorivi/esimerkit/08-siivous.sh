#!/usr/bin/env bash
# Lokien siivous: yli viikon vanhat pakataan, yli 30 päivän poistetaan.
set -euo pipefail
export LC_ALL=C

mkdir lokit
for paivat in 1 5 10 20 40 60; do
    seq 1000 > "lokit/palvelu-$paivat.log"
    touch -d "$paivat days ago" "lokit/palvelu-$paivat.log"
done
touch -d '90 days ago' lokit/tarkea.txt

# @alku siivous
find lokit -name '*.log' -mtime +30 -print -delete | sort
find lokit -name '*.log' -mtime +7 -exec gzip {} +
ls lokit
# @loppu siivous
