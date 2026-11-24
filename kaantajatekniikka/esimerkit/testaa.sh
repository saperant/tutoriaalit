#!/usr/bin/env bash
# Kide-kääntäjän testit. Ajetaan esimerkit/Makefilestä.
#
#   ohjelmat/NIMI.kide   oikea ohjelma; tuloste verrataan tiedostoon
#                        NIMI.odotettu tulkilla ja käännettynä usealla
#                        valintayhdistelmällä (qemu-riscv64)
#   virheet/NIMI.kide    virheellinen ohjelma; virhetuloste verrataan
#                        tiedostoon NIMI.virhe (ajo_*: tulkin ajovirhe)
#   naytteet/            tekstissä näytetyt kääntäjän välitulosteet
#   vertailu/            GCC:n tuottama assembly vertailuksi
#
# Lopuksi satunnaiset ohjelmat (satunnainen.py) ajetaan tulkilla ja
# käännettyinä, ja tarkoituksella rikottu kääntäjä (KIDE_VIKA) on
# saatava kiinni samoilla ohjelmilla.
#
#   ./testaa.sh             kaikki testit
#   ./testaa.sh --naytteet  kirjoittaa naytteet/ ja vertailu/ uudelleen
set -euo pipefail
cd "$(dirname "$0")"

GCC_KIDE=build/gcc/kide
CLANG_KIDE=build/clang/kide
VIKA_KIDE=build/vika/kide
AJO=build/ajonaikainen.o
CC_RV=riscv64-linux-gnu-gcc
SATUNNAISIA=${SATUNNAISIA:-40}
TYO=build/testit
mkdir -p "$TYO"

virheita=0
virhe() { echo "VIRHE: $*" >&2; virheita=$((virheita + 1)); }

# vertaa NIMI ODOTETTU SAATU
vertaa() {
    if ! diff -u "$2" "$3" > "$3.diff"; then
        virhe "$1: tuloste poikkeaa odotetusta"
        head -20 "$3.diff" >&2
    fi
}

# @alku kaanna
# kaanna_ja_aja KIDE LÄHDE ULOS [VALINNAT...]: kääntää, linkittää
# ajonaikaisen kirjaston kanssa ja ajaa ohjelman QEMU:ssa.
kaanna_ja_aja() {
    local kide=$1 lahde=$2 ulos=$3
    shift 3
    "$kide" "$@" "$lahde" > "$ulos.s"
    "$CC_RV" -static -o "$ulos" "$ulos.s" "$AJO"
    timeout 30 qemu-riscv64 "$ulos"
}
# @loppu kaanna

# Kääntäjän tulosteet, jotka näytetään tekstissä: nimi|valinnat|lähde.
SUMMA=naytteet/summa.kide
NAYTTEET=(
    "tokenit|--vaihe=tokenit|naytteet/pieni.kide"
    "ast-kertoma|--vaihe=ast|ohjelmat/kertoma.kide"
    "ast-presedenssi|--vaihe=ast|naytteet/presedenssi.kide"
    "ir-kertoma|--vaihe=ir -O0|ohjelmat/kertoma.kide"
    "ir-ehto|--vaihe=ir -O0|naytteet/ehto.kide"
    "passit-nelio|--vaihe=passit --funktio=nelio|naytteet/vakiot.kide"
    "ir-vakiot-O0|--vaihe=ir -O0 --funktio=main|naytteet/vakiot.kide"
    "ir-vakiot|--vaihe=ir --funktio=main|naytteet/vakiot.kide"
    "ir-summa|--vaihe=ir --funktio=summa|$SUMMA"
    "elavyys-summa|--vaihe=elavyys --funktio=summa|$SUMMA"
    "dominanssi-summa|--vaihe=dominanssi --funktio=summa|$SUMMA"
    "ssa-summa|--vaihe=ssa --funktio=summa|$SUMMA"
    "valit-summa|--vaihe=valit --funktio=summa|$SUMMA"
    "valit-summa-2|--vaihe=valit --rekistereita=2 --funktio=summa|$SUMMA"
    "asm-pino|-O0 --varaus=pino --funktio=nelioiden_summa|naytteet/nelio.kide"
    "asm-lineaarinen|-O1 --funktio=nelioiden_summa|naytteet/nelio.kide"
    "asm-kertoma|-O1 --funktio=kertoma|ohjelmat/kertoma.kide"
)

# GCC:n tuloste ilman ymmärtämisen kannalta turhia direktiivejä.
siisti() {
    local turhat='file|ident|size|type|attribute|option|p2align|align|cfi_'
    grep -Ev $'^\t\\.('"$turhat"$')|note\\.GNU-stack|^\\.LF[BE][0-9]+:' |
        sed -E 's/\t/    /g'
}

gcc_naytteet() { # HAKEMISTO
    for taso in O0 O2; do
        "$CC_RV" "-$taso" -S -o - -fno-asynchronous-unwind-tables \
            -fno-ident vertailu/kertoma.c | siisti > "$1/kertoma-$taso.s"
    done
}

if [[ ${1:-} == --naytteet ]]; then
    for n in "${NAYTTEET[@]}"; do
        IFS='|' read -r nimi valinnat lahde <<< "$n"
        # shellcheck disable=SC2086  # valinnat ovat erillisiä sanoja
        "$GCC_KIDE" $valinnat "$lahde" > "naytteet/$nimi.txt"
    done
    for p in ohjelmat/*.kide; do
        "$GCC_KIDE" --vaihe=aja "$p" > "${p%.kide}.odotettu"
    done
    gcc_naytteet vertailu
    echo "Näytteet kirjoitettu."
    exit 0
fi

# 1. Oikeat ohjelmat: tulkki ja käännetty ohjelma eri valinnoin.
# @alku valinnat
VALINNAT=("-O0 --varaus=pino" "-O1 --varaus=pino" "-O0" "-O1"
          "-O1 --rekistereita=2" "-O1 --rekistereita=1")
# @loppu valinnat
ohjelmia=0
for p in ohjelmat/*.kide; do
    nimi=$(basename "$p" .kide)
    odotettu=ohjelmat/$nimi.odotettu
    for kide in "$GCC_KIDE" "$CLANG_KIDE"; do
        "$kide" --vaihe=aja "$p" > "$TYO/$nimi.tulkki" ||
            virhe "$nimi: tulkki päättyi virheeseen"
        vertaa "$nimi (tulkki, $kide)" "$odotettu" "$TYO/$nimi.tulkki"
    done
    for v in "${VALINNAT[@]}"; do
        # shellcheck disable=SC2086
        kaanna_ja_aja "$GCC_KIDE" "$p" "$TYO/$nimi" $v > "$TYO/$nimi.ajo" ||
            virhe "$nimi ($v): käännetty ohjelma päättyi virheeseen"
        vertaa "$nimi ($v)" "$odotettu" "$TYO/$nimi.ajo"
    done
    kaanna_ja_aja "$CLANG_KIDE" "$p" "$TYO/$nimi" > "$TYO/$nimi.ajo"
    vertaa "$nimi (clang)" "$odotettu" "$TYO/$nimi.ajo"
    ohjelmia=$((ohjelmia + 1))
done

# 2. Virheelliset ohjelmat: oikeat virheilmoitukset ja paluuarvo.
virheohjelmia=0
for p in virheet/*.kide; do
    tiedosto=$(basename "$p")
    nimi=${tiedosto%.kide}
    vaihe=asm odotettu_paluu=1
    if [[ $nimi == ajo_* ]]; then vaihe=aja odotettu_paluu=3; fi
    for kide in "$GCC_KIDE" "$CLANG_KIDE"; do
        paluu=0
        (cd virheet && "../$kide" --vaihe=$vaihe "$tiedosto") \
            > /dev/null 2> "$TYO/$nimi.virhe" || paluu=$?
        [[ $paluu == "$odotettu_paluu" ]] ||
            virhe "$nimi: paluuarvo $paluu, odotettiin $odotettu_paluu"
        vertaa "$nimi" "virheet/$nimi.virhe" "$TYO/$nimi.virhe"
    done
    virheohjelmia=$((virheohjelmia + 1))
done

# 3. Tekstissä näytetyt välitulosteet ja GCC:n vertailukoodi.
for n in "${NAYTTEET[@]}"; do
    IFS='|' read -r nimi valinnat lahde <<< "$n"
    # shellcheck disable=SC2086
    "$GCC_KIDE" $valinnat "$lahde" > "$TYO/$nimi.txt"
    vertaa "näyte $nimi" "naytteet/$nimi.txt" "$TYO/$nimi.txt"
done
mkdir -p "$TYO/vertailu"
gcc_naytteet "$TYO/vertailu"
for taso in O0 O2; do
    vertaa "GCC -$taso" "vertailu/kertoma-$taso.s" \
        "$TYO/vertailu/kertoma-$taso.s"
done
kaanna_ja_aja "$GCC_KIDE" naytteet/summa.kide "$TYO/summa" > "$TYO/summa.ajo"
echo 18 | vertaa "summa" - "$TYO/summa.ajo"

# @alku satunnaiset
# 4. Differentiaalitestaus: tulkki on viitetoteutus, ja käännetyn
#    ohjelman on tulostettava täsmälleen sama.
for siemen in $(seq 1 "$SATUNNAISIA"); do
    s=$TYO/satunnainen-$siemen
    python3 satunnainen.py "$siemen" > "$s.kide"
    "$GCC_KIDE" --vaihe=aja "$s.kide" > "$s.tulkki"
    for v in "-O0 --varaus=pino" "-O1" "-O1 --rekistereita=2"; do
        # shellcheck disable=SC2086
        kaanna_ja_aja "$GCC_KIDE" "$s.kide" "$s" $v > "$s.ajo" ||
            virhe "siemen $siemen ($v): ajo päättyi virheeseen"
        cmp -s "$s.tulkki" "$s.ajo" ||
            virhe "siemen $siemen ($v): tulkki ja käännös eroavat"
    done
done
# @loppu satunnaiset

# 5. Testien teho: rikotun kääntäjän (<= käännetään kuten <) virheen on
#    näyttävä samoista satunnaisohjelmista.
loydetty=0 ensimmainen=
for siemen in $(seq 1 "$SATUNNAISIA"); do
    s=$TYO/satunnainen-$siemen
    kaanna_ja_aja "$VIKA_KIDE" "$s.kide" "$s-vika" -O1 > "$s.vika" || true
    if ! cmp -s "$s.tulkki" "$s.vika"; then
        loydetty=$((loydetty + 1))
        ensimmainen=${ensimmainen:-$siemen}
    fi
done
if [[ $loydetty == 0 ]]; then
    virhe "satunnaistestit eivät löytäneet tarkoituksellista vikaa"
else
    echo "Vika löytyi $loydetty/$SATUNNAISIA ohjelmasta" \
         "(ensimmäinen: siemen $ensimmainen)."
fi

if [[ $virheita -gt 0 ]]; then
    echo "VIRHEITÄ: $virheita" >&2
    exit 1
fi
echo "OK: $ohjelmia ohjelmaa ${#VALINNAT[@]}+3 tavalla," \
     "$virheohjelmia virheohjelmaa, ${#NAYTTEET[@]} näytettä," \
     "$SATUNNAISIA satunnaisohjelmaa."
