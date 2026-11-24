#!/usr/bin/env bash
# Ajaa kolme mallia ytimien määrillä 1-32 ja varausmallin kvantilla.
set -euo pipefail
# shellcheck disable=SC2086  # CXXFLAGS ja SYSTEMC ovat listoja
$CXX $CXXFLAGS "$LAHDE/main.cpp" $SYSTEMC -o ohjelma
echo "malli   K  kv.   aika us   GB/s viive ns  aktivointeja"
for malli in lt varaus sykli; do
    for k in 1 2 4 8 16 32; do
        ./ohjelma "$malli" "$k"
    done
done
./ohjelma varaus 16 1000
