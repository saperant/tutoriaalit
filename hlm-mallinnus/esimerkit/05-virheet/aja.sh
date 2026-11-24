#!/usr/bin/env bash
# Kääntää ohjelman ja ajaa sen kolmella virhetapauksella.
set -euo pipefail
# shellcheck disable=SC2086  # CXXFLAGS ja SYSTEMC ovat listoja
$CXX $CXXFLAGS "$LAHDE/main.cpp" $SYSTEMC -o ohjelma
for tapaus in 1 2 3; do
    echo "--- tapaus $tapaus"
    ./ohjelma "$tapaus"
done
