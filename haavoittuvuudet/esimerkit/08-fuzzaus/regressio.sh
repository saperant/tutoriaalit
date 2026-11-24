#!/usr/bin/env bash
# Regressiotesti: ajaa korjatun kohteen jokaisella korpuksen ja
# löydösten syötteellä kerran. libFuzzer ajaa tiedostoargumentit
# sellaisenaan ilman fuzzausta.
set -euo pipefail
# @alku regressio
kohde=$1
shift
"$kohde" "$@" > regressio.log 2>&1
echo "regressiotestit: $# syötettä, ei kaatumisia"
# @loppu regressio
