#!/usr/bin/env bash
# Käyttö: tarkista.sh raportti tuloste [kaikki|otsikko]
# Jokaisen raportin rivin on löydyttävä tulosteesta rivin alusta;
# "..." vastaa mitä tahansa tekstiä. Tilassa "otsikko" tarkistetaan vain
# WARNING-rivi (kun pinoja ei ole symboloitu).
set -euo pipefail
raportti=$1
tuloste=$2
tila=${3:-kaikki}
virheita=0
while IFS= read -r rivi; do
    [[ -z $rivi ]] && continue
    if [[ $tila == otsikko && $rivi != WARNING:* ]]; then
        continue
    fi
    # shellcheck disable=SC2016  # $ on sed-lausekkeessa kirjaimellinen
    malli=$(printf '%s' "$rivi" | sed -e 's/[][\.*^$(){}?+|]/\\&/g' \
                                     -e 's/\\\.\\\.\\\./.*/g')
    if ! grep -qE -- "^$malli" "$tuloste"; then
        echo "puuttuu: $rivi"
        virheita=$((virheita + 1))
    fi
done < "$raportti"
exit $((virheita > 0))
