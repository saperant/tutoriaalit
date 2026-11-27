#!/usr/bin/env bash
# Kide-kääntäjän testit. Ajetaan esimerkit/Makefilestä.
#
#   ohjelmat/NIMI.kide   oikea ohjelma; tuloste verrataan tiedostoon
#                        NIMI.odotettu tulkilla ja käännettynä usealla
#                        valintayhdistelmällä (qemu-riscv64)
#   virheet/NIMI.kide    virheellinen ohjelma; virhetuloste verrataan
#                        tiedostoon NIMI.virhe (ajo_*: tulkin ajovirhe)
#   naytteet/            tekstissä näytetyt kääntäjän välitulosteet
#   passit/NIMI.ir       yhden passin testi välikielenä: ensimmäinen rivi
#                        nimeää passit, tulos verrataan tiedostoon
#                        NIMI.odotettu ja ajon tuloste tiedostoon
#                        NIMI.tuloste (jos on); NIMI.virhe on odotettu
#                        virheilmoitus
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
LASKE=naytteet/laske.kide
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
    "ir-laske|--vaihe=ir --funktio=laske|naytteet/laske.kide"
    "ssa-laske|--vaihe=ssa --funktio=laske|naytteet/laske.kide"
    "ssa-laske-O2|--vaihe=ssa -O2 --funktio=laske|naytteet/laske.kide"
    "ssapassit-laske|--vaihe=ssapassit -O2 --funktio=laske|$LASKE"
    "ir-laske-O2|--vaihe=ir -O2 --funktio=laske|naytteet/laske.kide"
    "asm-kertoma-O2|-O2 --funktio=kertoma|ohjelmat/kertoma.kide"
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

# @alku passitesti
# passitesti TIEDOSTO.ir HAKEMISTO: ajaa tiedoston ensimmäisellä rivillä
# nimetyt passit ja kirjoittaa tulokset hakemistoon: välikieli (.odotettu),
# virheilmoitus (.virhe) ja käännetyn ohjelman tuloste (.tuloste), jos
# tiedostossa on main-funktio.
passitesti() {
    local t=$1 nimi passit
    nimi=$(basename "$t" .ir)
    passit=$(sed -n '1s/^; passit: //p' "$t")
    if ! (cd passit && "../$GCC_KIDE" --vaihe=ir --passit="$passit" \
            "$nimi.ir") > "$2/$nimi.odotettu" 2> "$2/$nimi.virhe"; then
        rm "$2/$nimi.odotettu"
        return
    fi
    rm "$2/$nimi.virhe"
    if grep -q '^fn main' "$t"; then
        kaanna_ja_aja "$GCC_KIDE" "$t" "$TYO/passi-$nimi" \
            --passit="$passit" > "$2/$nimi.tuloste"
    fi
}
# @loppu passitesti

# @alku mittaus
# kaskyja TASO LÄHDE: käskyjen määrä koodissa ja suoritettujen käskyjen
# määrä. Valinnalla --laske käännetty ohjelma laskee käskynsä itse.
kaskyja() {
    local koodissa suoritettu
    koodissa=$("$GCC_KIDE" "$1" "$2" | grep -c '^    [a-z]')
    suoritettu=$(kaanna_ja_aja "$GCC_KIDE" "$2" "$TYO/mittaus" "$1" --laske \
        2>&1 > /dev/null | sed 's/[^0-9]//g')
    echo "$koodissa $suoritettu"
}

mittaa() {
    echo "ohjelma      koodissa  koodissa   suoritettu   suoritettu  muutos"
    echo "                  -O1       -O2          -O1          -O2"
    for p in ohjelmat/*.kide naytteet/summa.kide naytteet/laske.kide; do
        read -r k1 s1 <<< "$(kaskyja -O1 "$p")"
        read -r k2 s2 <<< "$(kaskyja -O2 "$p")"
        awk -v n="$(basename "$p" .kide)" -v k1="$k1" -v k2="$k2" \
            -v s1="$s1" -v s2="$s2" 'BEGIN {
                printf "%-12s %8d  %8d  %11d  %11d  %+5.1f %%\n",
                       n, k1, k2, s1, s2, (s2 - s1) * 100 / s1 }'
    done
}
# @loppu mittaus

if [[ ${1:-} == --naytteet ]]; then
    for n in "${NAYTTEET[@]}"; do
        IFS='|' read -r nimi valinnat lahde <<< "$n"
        # shellcheck disable=SC2086  # valinnat ovat erillisiä sanoja
        "$GCC_KIDE" $valinnat "$lahde" > "naytteet/$nimi.txt"
    done
    for p in ohjelmat/*.kide; do
        "$GCC_KIDE" --vaihe=aja "$p" > "${p%.kide}.odotettu"
    done
    rm -f passit/*.odotettu passit/*.virhe passit/*.tuloste
    for t in passit/*.ir; do passitesti "$t" passit; done
    mittaa > naytteet/mittaus.txt
    gcc_naytteet vertailu
    echo "Näytteet kirjoitettu."
    exit 0
fi

# 1. Oikeat ohjelmat: tulkki ja käännetty ohjelma eri valinnoin.
# @alku valinnat
VALINNAT=("-O0 --varaus=pino" "-O1 --varaus=pino" "-O0" "-O1"
          "-O1 --rekistereita=2" "-O1 --rekistereita=1"
          "-O2" "-O2 --varaus=pino" "-O2 --rekistereita=2")
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
    for v in -O1 -O2; do
        kaanna_ja_aja "$CLANG_KIDE" "$p" "$TYO/$nimi" $v > "$TYO/$nimi.ajo"
        vertaa "$nimi (clang, $v)" "$odotettu" "$TYO/$nimi.ajo"
    done
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

# 4. Passien yksikkötestit välikielitiedostoista ja -O2:n mittaus.
passitesteja=0
mkdir -p "$TYO/passit"
rm -f "$TYO"/passit/*
for t in passit/*.ir; do
    passitesti "$t" "$TYO/passit"
    passitesteja=$((passitesteja + 1))
done
for o in passit/*.odotettu passit/*.virhe passit/*.tuloste; do
    if [[ -f $TYO/$o ]]; then
        vertaa "passi $(basename "$o")" "$o" "$TYO/$o"
    else
        virhe "passi $(basename "$o"): tulosta ei syntynyt"
    fi
done
[[ $(find "$TYO/passit" -type f ! -name '*.diff' | wc -l) == \
   $(find passit -type f ! -name '*.ir' | wc -l) ]] ||
    virhe "passit/: testi tuotti tiedoston, jota ei odotettu"
mittaa > "$TYO/mittaus.txt"
vertaa "mittaus" naytteet/mittaus.txt "$TYO/mittaus.txt"

# @alku satunnaiset
# 5. Differentiaalitestaus: tulkki on viitetoteutus, ja käännetyn
#    ohjelman on tulostettava täsmälleen sama.
for siemen in $(seq 1 "$SATUNNAISIA"); do
    s=$TYO/satunnainen-$siemen
    python3 satunnainen.py "$siemen" > "$s.kide"
    "$GCC_KIDE" --vaihe=aja "$s.kide" > "$s.tulkki"
    for v in "-O0 --varaus=pino" "-O1" "-O1 --rekistereita=2" \
             "-O2" "-O2 --rekistereita=2"; do
        # shellcheck disable=SC2086
        kaanna_ja_aja "$GCC_KIDE" "$s.kide" "$s" $v > "$s.ajo" ||
            virhe "siemen $siemen ($v): ajo päättyi virheeseen"
        cmp -s "$s.tulkki" "$s.ajo" ||
            virhe "siemen $siemen ($v): tulkki ja käännös eroavat"
    done
done
# @loppu satunnaiset

# 6. Testien teho: rikotun kääntäjän (<= käännetään kuten <) virheen on
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
echo "OK: $ohjelmia ohjelmaa ${#VALINNAT[@]}+4 tavalla," \
     "$virheohjelmia virheohjelmaa, ${#NAYTTEET[@]} näytettä," \
     "$passitesteja passitestiä, $SATUNNAISIA satunnaisohjelmaa."
