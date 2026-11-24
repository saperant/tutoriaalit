#!/usr/bin/env bash
# Kääntää, ajaa ja tarkistaa esimerkit.
#
# Jokainen esimerkki on hakemisto NN-nimi/, jossa voi olla
#   main.c ja muut *.c   C-lähteet (kaikille arkkitehtuureille)
#   x86.S, rv.S          arkkitehtuurikohtainen assembly
#   liput                lisävalitsimet kääntäjälle (yksi rivi)
#   arkkitehtuurit       ajettavat arkkitehtuurit (oletus: x86 rv)
#   odotettu             odotettu tuloste, tai
#   odotettu-x86, odotettu-rv  arkkitehtuurikohtaiset tulosteet
#   tarkistus.sh         lisätarkistus (objdump, readelf ym.); sen
#                        tuloste verrataan tiedostoon tarkistus.odotettu
#
# Kaikki ohjelmat käännetään -O2:lla ja linkitetään staattisesti, jotta
# QEMU ei tarvitse RISC-V-version jaettuja kirjastoja.
set -euo pipefail
cd "$(dirname "$0")"

CC_X86=$(command -v gcc-14 || command -v gcc)
export CC_X86
export CC_RV=riscv64-linux-gnu-gcc
export OBJDUMP_RV=riscv64-linux-gnu-objdump
export READELF_RV=riscv64-linux-gnu-readelf
# RISC-V-vektorilaajennus (V) päälle intrinsics-esimerkkiä varten.
export QEMU_CPU=rv64,v=true,vlen=128,vext_spec=v1.0
export CFLAGS="-O2 -std=c17 -Wall -Wextra -Werror"

virheita=0
virhe() { echo "VIRHE: $*" >&2; virheita=$((virheita + 1)); }

vertaa() { # NIMI ODOTETTU SAATU
    if ! diff -u "$2" "$3" > "$3.diff"; then
        virhe "$1: tuloste poikkeaa odotetusta"
        cat "$3.diff" >&2
    fi
}

for hak in [0-9][0-9]-*/; do
    hak=${hak%/}
    rak=build/$hak
    mkdir -p "$rak"
    arkit=(x86 rv)
    [[ -f $hak/arkkitehtuurit ]] && read -ra arkit < "$hak/arkkitehtuurit"
    lahteet_c=("$hak"/*.c)
    [[ -e ${lahteet_c[0]} ]] || lahteet_c=()
    if ((${#lahteet_c[@]})); then
        for ark in "${arkit[@]}"; do
            if [[ $ark == x86 ]]; then cc=$CC_X86; else cc=$CC_RV; fi
            lahteet=("${lahteet_c[@]}")
            [[ -f $hak/$ark.S ]] && lahteet+=("$hak/$ark.S")
            liput=()
            [[ -f $hak/liput ]] && read -ra liput < "$hak/liput"
            [[ -f $hak/liput-$ark ]] && read -ra lisa < "$hak/liput-$ark" &&
                liput+=("${lisa[@]}")
            # shellcheck disable=SC2086
            "$cc" $CFLAGS "${liput[@]}" -static -o "$rak/$ark" \
                "${lahteet[@]}"
            if [[ $ark == x86 ]]; then
                ajo=("$rak/$ark")
            else
                ajo=(qemu-riscv64 "$rak/$ark")
            fi
            if ! "${ajo[@]}" > "$rak/$ark.txt"; then
                virhe "$hak ($ark): paluuarvo ei ole 0"
                continue
            fi
            odotettu=$hak/odotettu
            [[ -f $hak/odotettu-$ark ]] && odotettu=$hak/odotettu-$ark
            vertaa "$hak ($ark)" "$odotettu" "$rak/$ark.txt"
        done
    fi
    if [[ -f $hak/tarkistus.sh ]]; then
        if ! RAK=$rak bash "$hak/tarkistus.sh" > "$rak/tarkistus.txt"; then
            virhe "$hak: tarkistus.sh epäonnistui"
            continue
        fi
        vertaa "$hak (tarkistus)" "$hak/tarkistus.odotettu" \
            "$rak/tarkistus.txt"
    fi
done

if ((virheita)); then
    echo "VIRHEITÄ: $virheita" >&2
    exit 1
fi
esimerkit=([0-9][0-9]-*/)
echo "OK: ${#esimerkit[@]} esimerkkiä x86-64:llä ja RISC-V:llä"
