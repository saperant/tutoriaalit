#!/usr/bin/env bash
# Fuzzaus libFuzzerilla ja AFL++:lla, löydösten minimointi ja
# regressiotestit.
source ./yhteinen.sh

# @alku kaanna
FUZZ=(-std=c23 -g -O1 "-fsanitize=fuzzer,address,undefined"
      -fno-sanitize-recover=all)
"$CLANG" "${FUZZ[@]}" tlv.c fuzz_tlv.c -o fuzz-0
# @loppu kaanna
"$CLANG" "${FUZZ[@]}" -DKORJAUS=1 tlv.c fuzz_tlv.c -o fuzz-1
"$CLANG" "${FUZZ[@]}" -DKORJAUS=2 tlv.c fuzz_tlv.c -o fuzz-2

# sumenna KOHDE NIMI: fuzzaa kiinteällä siemenellä ja rajatulla
# ajomäärällä tuoreesta korpuksen kopiosta. Löydös tallentuu nimellä
# NIMI. Ajo ei ole täysin toistettava (löydöksen tavut ja korpuksen koko
# vaihtelevat), joten tulostetaan vain virheen laji ja kohta.
sumenna() {
    rm -rf tyokorpus && cp -r korpus tyokorpus
    # @alku sumenna
    "$1" -seed=1 -runs=500000 -max_len=64 -exact_artifact_path="$2" \
        tyokorpus > "$2.log" 2>&1 || true
    # @loppu sumenna
    if [[ -f $2 ]]; then
        echo "löydös tallennettu: $2"
        python3 raportti.py < "$2.log" | sed -E 's/index [0-9]+/index N/'
    elif (($(find tyokorpus -type f | wc -l) > 2)); then
        echo "ei löydöksiä; korpus kasvoi uusilla syötteillä"
    fi
}

otsikko "kierros 1: alkuperäinen jäsennin"
sumenna ./fuzz-0 loydos-1
otsikko "minimointi"
# @alku minimoi
./fuzz-0 -minimize_crash=1 -runs=2000 -exact_artifact_path=minimi-1 \
    loydos-1 > minimi.log 2>&1 || true
# @loppu minimoi
# Minimointi käynnistää aliprosesseja omilla siemenillään, joten
# tulos vaihtelee: tarkistetaan vain, että syöte lyheni ja kaatuu
# edelleen samassa kohdassa.
if (($(wc -c < minimi-1) < $(wc -c < loydos-1))); then
    echo "minimoitu syöte on lyhyempi"
fi
./fuzz-0 minimi-1 > toisto.log 2>&1 || true
python3 raportti.py < toisto.log | sed -E 's/index [0-9]+/index N/'
otsikko "kierros 2: nimen tarkistus korjattu"
sumenna ./fuzz-1 loydos-2
otsikko "kierros 3: molemmat korjattu"
sumenna ./fuzz-2 loydos-3
otsikko "regressiotestit"
./regressio.sh ./fuzz-2 minimi-1 loydos-2 korpus/*

otsikko "AFL++"
# @alku afl
export AFL_SKIP_CPUFREQ=1 AFL_NO_AFFINITY=1 AFL_NO_UI=1 \
    AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1 AFL_BENCH_UNTIL_CRASH=1 \
    AFL_QUIET=1
afl-clang-fast -std=c2x -g -O1 -fsanitize=fuzzer tlv.c fuzz_tlv.c \
    -o fuzz-afl
env -u ASAN_OPTIONS -u UBSAN_OPTIONS timeout 120 \
    afl-fuzz -s 1 -V 60 -i korpus -o afl-tulos -- ./fuzz-afl \
    > afl.log 2>&1 || true
# @loppu afl
loydokset=(afl-tulos/default/crashes/id:*)
if [[ -f ${loydokset[0]} ]]; then
    echo "AFL++ löysi kaatuvan syötteen"
    if ! ./fuzz-0 "${loydokset[0]}" > afl-toisto.log 2>&1; then
        echo "syöte kaatuu myös sanitoijakäännöksessä"
    fi
else
    echo "AFL++ ei löytänyt kaatumista aikarajassa"
    tail -5 afl.log
fi
