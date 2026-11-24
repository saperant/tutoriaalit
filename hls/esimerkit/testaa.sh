#!/usr/bin/env bash
# Ajaa esimerkin vuon ja vertaa tulosteen tiedostoon odotettu.
#
# Käyttö:  ./testaa.sh 01-mac [02-... ...]
#
# Esimerkin hakemistossa on tiedosto asetukset, jonka jokainen rivi on
# yksi minihls-ajo (lähde ja valitsimet). Jos hakemistossa on testi.cpp,
# jokaisesta ajosta tehdään myös
#   1. C-simulaatio: testi.cpp käännetään niin, että makro YDIN on
#      lähteen nimi, ja ajetaan (testivektorit),
#   2. Verilatorin lint tuotetulle RTL:lle ja
#   3. C/RTL-yhteissimulaatio tuotetulla testipenkillä.
# Jos hakemistossa on lähteen nimeä vastaava mallitiedosto mac.v tai
# mac.tb.sv (lähteelle mac.cpp), tuotetun RTL:n tai testipenkin on oltava
# sama. Tiedosto yosys pyytää resurssiraportin. Tiedosto kaatuu
# tarkoittaa, että minihls:n odotetaan ilmoittavan virheestä, ja
# csim-kaatuu, että C-simulaation odotetaan pysähtyvän sanitoijaan.
set -euo pipefail
cd "$(dirname "$0")"
# Verilator kutsuu makea: ylemmän maken valitsimet eivät kuulu sille.
unset MAKEFLAGS MFLAGS MAKELEVEL
export PYTHONDONTWRITEBYTECODE=1

# @alku asetukset
export CXX=${CXX:-g++-14}
# shellcheck disable=SC2054  # pilkku kuuluu valitsimeen
CXXFLAGS=(-std=c++20 -Wall -Wextra -Werror -Wno-unknown-pragmas
          -Wno-unused-label -fsanitize=address,undefined
          -fno-sanitize-recover=all -Iyhteinen)
VERILATOR_LINT=(--lint-only -Wall -Wno-UNUSEDSIGNAL)
# @loppu asetukset

aja() {
    local hak=$1 tyo=$2 n=0 rivi
    while read -r -a rivi; do
        # Merkinnät rajaavat kunkin ajon tulosteen kirjaa varten.
        ((n == 0)) || echo "# @loppu ajo$n"
        n=$((n + 1))
        echo "# @alku ajo$n"
        local lahde=${rivi[0]} valitsimet=("${rivi[@]:1}")
        local ulos=$tyo/ajo$n ylin
        ylin=$(sed -n 's/.*--top \([a-z_0-9]*\).*/\1/p' <<< "${rivi[*]}")
        echo "\$ minihls ${rivi[*]}"
        if ! python3 -m minihls "$hak/$lahde" "${valitsimet[@]}" \
                --ulos "$ulos"; then
            [[ -f $hak/kaatuu ]] || return 1
            continue
        fi
        local malli=$hak/${lahde%.cpp}.v
        if [[ -f $malli ]]; then
            # Mallitiedoston @alku- ja @loppu-merkinnät ovat kirjaa varten.
            grep -v -e '// @alku' -e '// @loppu' "$malli" |
                diff -u - "$ulos/$ylin.v" >&2 || return 1
        fi
        if [[ -f ${malli%.v}.tb.sv ]]; then
            grep -v -e '// @alku' -e '// @loppu' "${malli%.v}.tb.sv" |
                diff -u - "$ulos/tb.sv" >&2 || return 1
        fi
        if [[ -f $hak/yosys ]]; then
            echo "\$ yosys: $ylin"
            yosys -q -p "read_verilog $ulos/$ylin.v; hierarchy -top $ylin; \
                proc; opt; wreduce; opt_clean; tee -o $ulos/stat.txt \
                stat -width" > /dev/null ||
                return 1
            python3 tyokalut/yosys_stat.py "$ulos/stat.txt" || return 1
        fi
        [[ -f $hak/testi.cpp ]] || continue
        echo "\$ ./csim"
        "$CXX" "${CXXFLAGS[@]}" -I"$hak" -DYDIN="\"$lahde\"" \
            "$hak/testi.cpp" -o "$ulos/csim" || return 1
        if [[ -f $hak/csim-kaatuu ]]; then
            # Odotettu virhe: sanitoijan ilmoitus riveille taitettuna.
            (cd "$ulos" && ! ./csim 2>&1) | fold -s -w 78 |
                sed 's/ *$//' || return 1
            continue
        fi
        (cd "$ulos" && ./csim) || return 1
        echo "\$ verilator: C/RTL-yhteissimulaatio"
        verilator "${VERILATOR_LINT[@]}" "$ulos/$ylin.v" || return 1
        (cd "$ulos" && verilator --binary --timing -Wno-fatal -Wno-lint \
            tb.sv "$ylin.v" -o tb > verilator.log 2>&1) || return 1
        (cd "$ulos" && ./obj_dir/tb > tb.log) || return 1
        grep -v -F -e '- tb.sv:' "$ulos/tb.log"
    done < "$hak/asetukset"
    echo "# @loppu ajo$n"
}

virheita=0
for hak in "$@"; do
    hak=${hak%/}
    tyo=rakennus/$hak
    rm -rf "$tyo"
    mkdir -p "$tyo"
    if ! aja "$hak" "$tyo" > "$tyo.saatu" 2> "$tyo.virheet"; then
        echo "VIRHE: $hak: vuo epäonnistui" >&2
        cat "$tyo.saatu" "$tyo.virheet" >&2
        virheita=$((virheita + 1))
        continue
    fi
    if ! diff -u "$hak/odotettu" "$tyo.saatu" > "$tyo.diff"; then
        echo "VIRHE: $hak: tuloste poikkeaa odotetusta" >&2
        cat "$tyo.diff" "$tyo.virheet" >&2
        virheita=$((virheita + 1))
    fi
done
exit $((virheita > 0))
