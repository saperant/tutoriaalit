# Asetustiedoston lukija: AVAIN=arvo-rivit assosiatiiviseen taulukkoon
# ilman, että tiedostoa suoritetaan koodina.
# shellcheck shell=bash

# @alku lue
# lue_asetukset TIEDOSTO TAULUKKO
lue_asetukset() {
    local -n _kohde=$2
    local rivi avain arvo nro=0
    while IFS= read -r rivi || [[ -n $rivi ]]; do
        (( ++nro ))
        [[ $rivi =~ ^[[:space:]]*(#|$) ]] && continue
        if [[ ! $rivi =~ ^([A-Z_][A-Z0-9_]*)=(.*)$ ]]; then
            loki varoitus "$1:$nro: ohitetaan: $rivi"
            continue
        fi
        avain=${BASH_REMATCH[1]} arvo=${BASH_REMATCH[2]}
        _kohde["$avain"]=$arvo
    done < "$1"
}
# @loppu lue
