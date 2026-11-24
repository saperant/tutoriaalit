#!/usr/bin/env bash
# Ajaa saman mallin neljällä eri kvantilla (nanosekunteina).
set -euo pipefail
# shellcheck disable=SC2086  # CXXFLAGS ja SYSTEMC ovat listoja
$CXX $CXXFLAGS "$LAHDE/main.cpp" $SYSTEMC -o ohjelma
for kvantti in 0 100 1000 10000; do
    ./ohjelma "$kvantti"
done
