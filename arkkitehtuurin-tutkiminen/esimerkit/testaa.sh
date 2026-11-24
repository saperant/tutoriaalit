#!/usr/bin/env bash
# Kääntää ja ajaa C++-esimerkin ja vertaa tulosteen tiedostoon odotettu.
#
# Käyttö:  ./testaa.sh 05-muisti [06-ydin ...]
#
# Esimerkin NN-nimi/ .cpp-tiedostot käännetään ohjelmaksi
# build/NN-nimi/ohjelma, joka ajetaan hakemistossa build/NN-nimi/; sinne
# jäävät myös ohjelman kirjoittamat tiedostot (esim. jäljet). Jos
# hakemistossa on aja.sh, se kääntää ja ajaa esimerkin itse.
set -euo pipefail
cd "$(dirname "$0")"

# @alku asetukset
export CXX=${CXX:-g++-14}
# SystemC 2.3 on käännetty C++17:lle; muut esimerkit käännetään C++20:lla
# ja sanitoijilla.
VAROITUKSET="-O1 -Wall -Wextra -Werror"
SYSTEMC=$(pkg-config --cflags --libs systemc tlm)
export SYSTEMC
export SC_COPYRIGHT_MESSAGE=DISABLE
# @loppu asetukset

virheita=0
for hak in "$@"; do
    hak=${hak%/}
    tyo=build/$hak
    rm -rf "$tyo"
    mkdir -p "$tyo"
    saatu=build/$hak.saatu
    export LAHDE=$PWD/$hak
    if grep -q '#include <systemc>' "$hak"/*.cpp; then
        export CXXFLAGS="-std=c++17 $VAROITUKSET"
        lisa=$SYSTEMC
    else
        export CXXFLAGS="-std=c++20 $VAROITUKSET -fsanitize=address,undefined"
        lisa=""
    fi
    if [[ -f $hak/aja.sh ]]; then
        komento=(bash "$LAHDE/aja.sh")
    else
        # shellcheck disable=SC2086  # CXXFLAGS ja lisa ovat listoja
        $CXX $CXXFLAGS "$hak"/*.cpp $lisa -o "$tyo/ohjelma"
        komento=(./ohjelma)
    fi
    if ! (cd "$tyo" && "${komento[@]}") > "$saatu" 2>&1; then
        echo "VIRHE: $hak: ajo päättyi virheeseen" >&2
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
exit $((virheita > 0))
