#!/usr/bin/env bash
# Kokoaa, ajaa ja tarkistaa assembly-esimerkit.
#
# Jokainen esimerkki on hakemisto NN-nimi/, jossa voi olla
#   x86.S       x86-64-toteutus (GNU as, AT&T-syntaksi)
#   rv.S        RISC-V-toteutus (RV64GC)
#   main.c      C-pääohjelma; ilman sitä ohjelma linkitetään ilman
#               C-kirjastoa (-nostdlib) ja se alkaa symbolista _start
#   syote       ohjelman syöte
#   odotettu    odotettu tuloste molemmille arkkitehtuureille, tai
#   odotettu-x86, odotettu-rv  arkkitehtuurikohtaiset tulosteet
#
# Hakemiston *-kaatuu/ ohjelman on päätyttävä virheeseen (esimerkki
# yleisestä virheestä).
# Hakemisto *-tavut/ tarkistaa käskyjen konekielisen koodauksen
# (objdump). Hakemistojen *-c-rakenteet/ ja *-naytteet/ C-tiedostoista
# käännetään assembly-näytteet (*-x86.s, *-rv.s), joiden on vastattava
# versionhallinnassa olevia; --naytteet kirjoittaa ne uudelleen.
# Hakemiston tiedosto liput lisää näytteiden kääntäjävalitsimia.
set -euo pipefail
cd "$(dirname "$0")"

CC_X86=$(command -v gcc-14 || command -v gcc)
CC_RV=riscv64-linux-gnu-gcc
OBJDUMP_RV=riscv64-linux-gnu-objdump
# RISC-V-vektorilaajennus (V) päälle SIMD-esimerkkiä varten.
export QEMU_CPU=rv64,v=true,vlen=128,vext_spec=v1.0
CFLAGS=(-O2 -std=c17 -Wall -Wextra -Werror)
NAYTE=(-O2 -S -fno-asynchronous-unwind-tables -fcf-protection=none
       -fno-stack-protector -fno-ident -fno-tree-vectorize
       -fno-unwind-tables -fno-reorder-blocks-and-partition)
# Näytteet, joista käännetään myös optimoimaton (-O0) versio x86-64:lle.
O0_NAYTTEET=(taulukko)
kirjoita_naytteet=0
[[ ${1:-} == --naytteet ]] && kirjoita_naytteet=1

virheita=0
virhe() { echo "VIRHE: $*" >&2; virheita=$((virheita + 1)); }

# vertaa NIMI ODOTETTU SAATU
vertaa() {
    if ! diff -u "$2" "$3" > "$3.diff"; then
        virhe "$1: tuloste poikkeaa odotetusta"
        cat "$3.diff" >&2
    fi
}

# Kääntäjän tuloste ilman ohjelman ymmärtämisen kannalta turhia
# direktiivejä (tiedostonimi, symbolien tyypit ja koot, tasaukset).
siisti() {
    grep -Ev $'^\t\\.(file|ident|size|type|attribute|option|p2align|align|cfi_)|note\\.GNU-stack|^\\.LF[BE][0-9]+:' |
        sed -E 's/\t/    /g'
}

kokoa() { # ARK HAKEMISTO ULOS
    local ark=$1 hak=$2 ulos=$3 cc lahteet=()
    if [[ $ark == x86 ]]; then cc=$CC_X86; else cc=$CC_RV; fi
    [[ -f $hak/$ark.S ]] && lahteet+=("$hak/$ark.S")
    if [[ -f $hak/main.c ]]; then
        lahteet+=("$hak/main.c")
        for c in "$hak"/*.c; do
            [[ $c == "$hak/main.c" ]] || lahteet+=("$c")
        done
        "$cc" "${CFLAGS[@]}" -static -o "$ulos" "${lahteet[@]}"
    else
        "$cc" -nostdlib -static -o "$ulos" "${lahteet[@]}"
    fi
}

aja() { # ARK OHJELMA SYÖTE
    local syote=${3:-/dev/null}
    if [[ $1 == x86 ]]; then "$2" < "$syote"; else qemu-riscv64 "$2" < "$syote"; fi
}

for hak in [0-9][0-9]-*/; do
    hak=${hak%/}
    mkdir -p "build/$hak"
    case $hak in
    *-tavut)
        for ark in x86 rv; do
            if [[ $ark == x86 ]]; then cc=$CC_X86 od=objdump
            else cc=$CC_RV od=$OBJDUMP_RV; fi
            "$cc" -c -o "build/$hak/$ark.o" "$hak/$ark.S"
            # Disassemblerin omat rivinloppukommentit (# osoite <symboli>)
            # jätetään pois: linkittämättömässä tiedostossa ne
            # johtavat harhaan.
            "$od" -d "build/$hak/$ark.o" | tail -n +7 |
                sed -E 's/\t/    /g; s/ +# .*$//; s/ +$//' \
                > "build/$hak/$ark.txt"
            vertaa "$hak ($ark)" "$hak/odotettu-$ark" "build/$hak/$ark.txt"
        done
        continue ;;
    *-c-rakenteet | *-naytteet)
        lisaliput=()
        [[ -f $hak/liput ]] && read -ra lisaliput < "$hak/liput"
        for c in "$hak"/*.c; do
            nimi=$(basename "$c" .c)
            [[ $nimi == main ]] && continue
            versiot=(x86 rv)
            [[ " ${O0_NAYTTEET[*]} " == *" $nimi "* ]] && versiot+=(x86-O0)
            for v in "${versiot[@]}"; do
                cc=$CC_X86 lisa=()
                [[ $v == rv ]] && cc=$CC_RV
                [[ $v == x86-O0 ]] && lisa=(-O0)
                "$cc" "${NAYTE[@]}" "${lisaliput[@]}" "${lisa[@]}" \
                    -o - "$c" | siisti \
                    > "build/$hak/$nimi-$v.s"
                if ((kirjoita_naytteet)); then
                    cp "build/$hak/$nimi-$v.s" "$hak/$nimi-$v.s"
                else
                    vertaa "$hak ($nimi-$v.s)" "$hak/$nimi-$v.s" \
                        "build/$hak/$nimi-$v.s"
                fi
            done
        done ;;
    esac
    for ark in x86 rv; do
        # Arkkitehtuuri ajetaan, jos sille on toteutus tai esimerkki on
        # pelkkää C:tä.
        if [[ ! -f $hak/$ark.S ]]; then
            [[ -f $hak/main.c && ! -f $hak/x86.S && ! -f $hak/rv.S ]] ||
                continue
        fi
        ohjelma=build/$hak/$ark
        kokoa "$ark" "$hak" "$ohjelma"
        syote=
        [[ -f $hak/syote ]] && syote=$hak/syote
        if [[ $hak == *-kaatuu ]]; then
            # Tarkoituksellinen virhe: ohjelman on kaaduttava.
            if (aja "$ark" "$ohjelma" "$syote" > "$ohjelma.txt" 2>&1); then
                virhe "$hak ($ark): ohjelma ei kaatunut"
            fi
            continue
        fi
        if ! aja "$ark" "$ohjelma" "$syote" > "$ohjelma.txt"; then
            virhe "$hak ($ark): paluuarvo ei ole 0"
            continue
        fi
        odotettu=$hak/odotettu
        [[ -f $hak/odotettu-$ark ]] && odotettu=$hak/odotettu-$ark
        vertaa "$hak ($ark)" "$odotettu" "$ohjelma.txt"
    done
done

if ((virheita)); then
    echo "VIRHEITÄ: $virheita" >&2
    exit 1
fi
esimerkit=([0-9][0-9]-*/)
echo "OK: ${#esimerkit[@]} esimerkkiä x86-64:llä ja RISC-V:llä"
