#!/usr/bin/env bash
# Kääntää RTL:n Verilatorilla SystemC-moduuliksi, linkittää sen
# testipenkkiin ja ajaa vertailun. Toinen ajo käyttää RTL:n versiota,
# josta pyöristys puuttuu: vertailun pitää löytää ero.
set -euo pipefail

aja() {
    local nimi=$1 pyoristys=$2
    # Verilatorin tuloste ohjataan lokiin; se näytetään vain virheessä.
    if ! verilator --sc --exe --build -j 2 -Wall --top-module fir \
        -GPYORISTYS="$pyoristys" \
        -CFLAGS "-std=c++17 -DSC_INCLUDE_FX -Wall -Wextra" \
        --Mdir "obj_$nimi" -o testipenkki \
        "$LAHDE/fir.sv" "$LAHDE/testipenkki.cpp" > "$nimi.log" 2>&1; then
        cat "$nimi.log" >&2
        return 1
    fi
    echo "--- $nimi"
    if "./obj_$nimi/testipenkki"; then
        echo "  tulos: RTL vastaa mallia"
    else
        echo "  tulos: RTL ja malli eroavat"
    fi
}

aja oikea 1
aja katkaisu 0
