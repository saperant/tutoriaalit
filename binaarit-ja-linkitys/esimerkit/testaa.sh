#!/usr/bin/env bash
# Ajaa jokaisen esimerkkihakemiston NN-nimi/aja.sh-skriptin omassa
# työhakemistossaan build/NN-nimi/ ja vertaa tulosteen tiedostoon
# NN-nimi/odotettu. Skriptit tarkistetaan ShellCheckillä.
set -euo pipefail
cd "$(dirname "$0")"

virheita=0
shellcheck -x yhteinen.sh testaa.sh [0-9][0-9]-*/aja.sh

for hak in [0-9][0-9]-*/; do
    hak=${hak%/}
    rm -rf "build/$hak"
    mkdir -p "build/$hak"
    cp -r "$hak"/. "build/$hak"/
    cp yhteinen.sh "build/$hak"/
    saatu=$PWD/build/$hak.saatu
    if ! (cd "build/$hak" && bash ./aja.sh) > "$saatu" 2>&1; then
        echo "VIRHE: $hak: aja.sh päättyi virheeseen" >&2
        cat "$saatu" >&2
        virheita=$((virheita + 1))
        continue
    fi
    if ! diff -u "$hak/odotettu" "$saatu" > "$saatu.diff"; then
        echo "VIRHE: $hak: tuloste poikkeaa odotetusta" >&2
        cat "$saatu.diff" >&2
        virheita=$((virheita + 1))
    fi
done

maara=$(find . -maxdepth 1 -name '[0-9][0-9]-*' -type d | wc -l)
if ((virheita)); then
    echo "VIRHEITÄ: $virheita"
    exit 1
fi
echo "OK: $maara esimerkkiä"
