#!/usr/bin/env bash
# Putken jokainen osa ajetaan omassa alikuoressaan: silmukan sisällä
# tehdyt muuttujamuutokset katoavat, kun putki päättyy.
set -euo pipefail

laske_putkella() {
    local maara=0
    printf '%s\n' a b c | while IFS= read -r _; do
        maara=$((maara + 1))
    done
    # Tarkoituksellinen virhe havainnollistusta varten: ShellCheck
    # varoittaisi tästä (SC2031), joten varoitus vaimennetaan.
    # shellcheck disable=SC2031
    echo "putkella: $maara"
}

laske_prosessikorvauksella() {
    local maara=0
    while IFS= read -r _; do
        maara=$((maara + 1))
    done < <(printf '%s\n' a b c)
    echo "prosessikorvauksella: $maara"
}

laske_putkella
laske_prosessikorvauksella
