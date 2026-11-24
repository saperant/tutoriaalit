#!/usr/bin/env bash
# Kääntää ja ajaa esimerkin ja vertaa tulosteen tiedostoon odotettu.
#
# Käyttö:  ./testaa.sh 08-fir [09-tlm-muisti ...]
#          ./testaa.sh                (kaikki esimerkit)
#
# Esimerkin NN-nimi/ .cpp-tiedostot käännetään ohjelmaksi
# build/NN-nimi/ohjelma, joka ajetaan hakemistossa build/NN-nimi/.
# Jos hakemistossa on aja.sh, se rakentaa ja ajaa esimerkin itse; sille
# välitetään alla asetetut muuttujat.
set -euo pipefail
cd "$(dirname "$0")"

# @alku asetukset
# SystemC 2.3 on käännetty C++17:lle, ja kirjasto tarkistaa linkityksessä,
# että ohjelma käyttää samaa standardia.
export CXX=${CXX:-g++-14}
export CXXFLAGS="-std=c++17 -O1 -Wall -Wextra -Werror"
SYSTEMC=$(pkg-config --cflags --libs systemc tlm)
export SYSTEMC
# Ilman tätä SystemC tulostaa käynnistyessään tekijänoikeusilmoituksen.
export SC_COPYRIGHT_MESSAGE=DISABLE
# @loppu asetukset

if (($# == 0)); then
    set -- [0-9][0-9]-*/
fi

virheita=0
for hak in "$@"; do
    hak=${hak%/}
    tyo=build/$hak
    rm -rf "$tyo"
    mkdir -p "$tyo"
    saatu=$tyo.saatu
    export LAHDE=$PWD/$hak
    if [[ -f $hak/aja.sh ]]; then
        komento=(bash "$LAHDE/aja.sh")
    else
        # shellcheck disable=SC2086  # SYSTEMC ja CXXFLAGS ovat listoja
        $CXX $CXXFLAGS "$hak"/*.cpp $SYSTEMC -o "$tyo/ohjelma"
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
