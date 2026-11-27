#!/usr/bin/env bash
# Ajaa keskeytysesimerkin kolmella tavalla: tapahtumaloki, vertailu eri
# kvanteilla sekä koe ilman synkronointia mret-käskyssä.
set -euo pipefail
# shellcheck disable=SC2086  # CXXFLAGS ja SYSTEMC ovat listoja
$CXX $CXXFLAGS "$LAHDE/main.cpp" $SYSTEMC -o ohjelma

echo "== loki: kvantti 1000 ns, wfi, pääte päällä"
./ohjelma 1000 wfi loki

echo "== kvantin ja odotustavan vaikutus"
cat << 'OTSIKKO'
kvantti  tila     tikit  menetetyt      viive ns  käskyjä  synkr.  aika us
OTSIKKO
for kvantti in 0 1000 10000 50000; do
    for tila in kysely wfi; do
        ./ohjelma "$kvantti" "$tila"
    done
done

echo "== koe: kvantti 1000 ns, kysely"
./ohjelma 1000 kysely ei-synkronointia
