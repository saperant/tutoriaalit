#!/usr/bin/env bash
# Ajaa jokaisen esimerkkihakemiston NN-nimi/aja.sh-skriptin omassa
# työhakemistossaan build/NN-nimi/ ja vertaa tulosteen tiedostoon
# NN-nimi/odotettu. Skriptit tarkistetaan ShellCheckillä ja
# Python-työkalut ruffilla ja mypyllä.
set -euo pipefail
cd "$(dirname "$0")"
unset MAKEFLAGS MAKELEVEL

virheita=0
shellcheck -x yhteinen.sh testaa.sh [0-9][0-9]-*/*.sh
mapfile -t python < <(find . -name '*.py' -not -path './build/*' | sort)
ruff check --quiet --no-cache "${python[@]}"
mypy --strict --no-incremental --cache-dir=/dev/null "${python[@]}" \
    > build.mypy 2>&1 || { cat build.mypy; rm -f build.mypy; exit 1; }
rm -f build.mypy

ajot=()
for hak in [0-9][0-9]-*/; do
    hak=${hak%/}
    rm -rf "build/$hak"
    mkdir -p "build/$hak"
    cp -r "$hak"/. "build/$hak"/
    cp yhteinen.sh tyokalut/*.py "build/$hak"/
    (cd "build/$hak" && timeout 300 bash ./aja.sh) \
        > "build/$hak.saatu" 2>&1 &
    ajot+=("$!:$hak")
done

for ajo in "${ajot[@]}"; do
    pid=${ajo%%:*}
    hak=${ajo#*:}
    saatu=build/$hak.saatu
    if ! wait "$pid"; then
        echo "VIRHE: $hak: aja.sh päättyi virheeseen" >&2
        cat "$saatu" >&2
        virheita=$((virheita + 1))
        continue
    fi
    # Odotetun tulosteen @alku- ja @loppu-merkinnät rajaavat tekstissä
    # näytettäviä osia; ne eivät kuulu tulosteeseen.
    if ! grep -vE '^# @(alku|loppu) ' "$hak/odotettu" |
        diff -u - "$saatu" > "$saatu.diff"; then
        echo "VIRHE: $hak: tuloste poikkeaa odotetusta" >&2
        cat "$saatu.diff" >&2
        virheita=$((virheita + 1))
    fi
done

maara=${#ajot[@]}
if ((virheita)); then
    echo "VIRHEITÄ: $virheita"
    exit 1
fi
echo "OK: $maara esimerkkiä"
