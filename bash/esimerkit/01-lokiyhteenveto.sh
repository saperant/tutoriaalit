#!/usr/bin/env bash
# Tiivistää palvelun lokin: rivimäärät tasoittain ja virheiden rivit.
# Käyttö: lokiyhteenveto.sh < palvelu.log
set -euo pipefail

main() {
    local rivinro=0 rivi taso
    local -A maarat=()
    local virheet=()

    while IFS= read -r rivi; do
        rivinro=$((rivinro + 1))
        read -r _ taso _ <<< "$rivi"
        [[ -n ${taso:-} ]] || continue          # tyhjä rivi
        maarat[$taso]=$(( ${maarat[$taso]:-0} + 1 ))
        if [[ $taso == ERROR ]]; then
            virheet+=("$rivinro")
        fi
    done

    for taso in ERROR WARN INFO DEBUG; do
        printf '%-5s %3d\n' "$taso" "${maarat[$taso]:-0}"
    done
    if (( ${#virheet[@]} > 0 )); then
        printf 'Virheet riveillä: %s\n' "${virheet[*]}"
    fi
}

main "$@"
