#!/usr/bin/env bash
# `local muuttuja=$(komento)` peittää komennon paluuarvon: local
# onnistuu aina, joten virhe jää huomaamatta myös set -e:n kanssa.
set -euo pipefail

lue_asetus() {
    [[ -f asetukset.conf ]] || return 1
    cat asetukset.conf
}

kaynnista() {
    local asetus=$(lue_asetus)          # @virhe
    local asetus                        # erotetaan esittely ja sijoitus
    if ! asetus=$(lue_asetus); then
        echo "asetuksia ei löytynyt, käytetään oletuksia"
        asetus='oletus'
    fi
    echo "asetus: $asetus"
}

kaynnista
