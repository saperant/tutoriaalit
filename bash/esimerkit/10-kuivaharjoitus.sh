#!/usr/bin/env bash
# Kuivaharjoitus (dry run): -n tulostaa muuttavat komennot ajamatta
# niitä. Kaikki muuttavat komennot kulkevat yhden funktion kautta,
# joten tila ei voi unohtua yksittäisestä komennosta.
set -euo pipefail

# @alku aja
KUIVA=0

aja() {
    if (( KUIVA )); then
        printf 'kuiva:'
        printf ' %q' "$@"
        printf '\n'
    else
        "$@"
    fi
}
# @loppu aja

# @alku kaytto
while getopts ':n' valitsin; do
    case $valitsin in
        n) KUIVA=1 ;;
        *) echo "käyttö: ${0##*/} [-n] HAKEMISTO PÄIVIÄ" >&2; exit 2 ;;
    esac
done
shift $(( OPTIND - 1 ))
hakemisto=${1:?hakemisto puuttuu} paivia=${2:?päivien määrä puuttuu}

# Esimerkkiä varten luodaan vanhoja lokitiedostoja.
mkdir -p "$hakemisto"
touch -d '90 days ago' "$hakemisto/palvelu 3.log"
touch -d '45 days ago' "$hakemisto/palvelu 2.log"
touch "$hakemisto/palvelu 1.log"

while IFS= read -r -d '' tiedosto; do
    aja rm -- "$tiedosto"
done < <(find "$hakemisto" -name '*.log' -mtime "+$paivia" -print0 |
         sort -z)
echo "tiedostoja jäljellä: $(find "$hakemisto" -type f | wc -l)"
# @loppu kaytto
