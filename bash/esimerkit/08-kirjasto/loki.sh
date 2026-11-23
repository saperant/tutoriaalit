# Lokikirjasto: aikaleimatut viestit virhetulosteeseen.
# Ladataan komennolla source; ei suoriteta itsenäisesti.
# shellcheck shell=bash

# @alku suoja
[[ -n ${_LOKI_LADATTU:-} ]] && return 0
readonly _LOKI_LADATTU=1
# @loppu suoja

# @alku tasot
declare -grA _LOKI_TASOT=([virhe]=0 [varoitus]=1 [info]=2 [debug]=3)
LOKI_TASO=${LOKI_TASO:-info}

loki() {
    local taso=$1; shift
    (( _LOKI_TASOT[$taso] <= _LOKI_TASOT[$LOKI_TASO] )) || return 0
    printf '%s %-8s %s\n' "${LOKI_AIKA:-$(date +%T)}" "$taso" "$*" >&2
}
# @loppu tasot
