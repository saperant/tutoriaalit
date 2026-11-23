#!/usr/bin/env bash
# xargs -P ajaa komentoja rinnakkain tiedostolistasta. -0 käyttää
# nollatavua erottimena, joten välilyönnit ja rivinvaihdot nimissä
# eivät haittaa.
set -euo pipefail
export LC_ALL=C

mkdir -p lokit
for paiva in 01 02 03 04; do
    printf 'GET /\nPOST /api\nGET /\n' > "lokit/pääsy 2026-11-$paiva.log"
done

# @alku xargs
find lokit -name '*.log' -print0 |
    xargs -0 -P 4 -n 1 gzip -9
ls lokit
# @loppu xargs

# @alku funktio
laske() {
    printf '%s %d\n' "${1##*/}" "$(gzip -dc -- "$1" | grep -c '^GET')"
}
export -f laske
# Yksinkertaiset lainausmerkit ovat tarkoituksellisia: $1 laajennetaan
# vasta bash -c:n käynnistämässä kuoressa.
# shellcheck disable=SC2016
find lokit -name '*.gz' -print0 |
    xargs -0 -P 4 -I {} bash -c 'laske "$1"' _ {} |
    sort
# @loppu funktio
