#!/usr/bin/env bash
# INI-tiedoston osion arvo awkilla: tila muuttujassa.
set -euo pipefail
export LC_ALL=C

cat > palvelu.ini <<'INI'
[palvelin]
portti = 8080
osoite = 0.0.0.0

[tietokanta]
osoite = db1.sisainen
portti = 5432
INI

# @alku osio
hae() {   # hae TIEDOSTO OSIO AVAIN
    awk -F' *= *' -v osio="[$2]" -v avain="$3" '
        /^\[/      { sisalla = ($0 == osio); next }
        sisalla && $1 == avain { print $2; loytyi = 1; exit }
        END        { exit !loytyi }' "$1"
}
hae palvelu.ini tietokanta portti
hae palvelu.ini palvelin osoite
hae palvelu.ini tietokanta salasana || echo "ei löytynyt"
# @loppu osio
