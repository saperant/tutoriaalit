#!/usr/bin/env bash
# shellcheck disable=SC2038,SC2016  # naiivi tapa näytetään tarkoituksella
# Tiedostonimien turvallinen välitys: -print0 ja xargs -0.
set -euo pipefail
export LC_ALL=C

mkdir raportit
seq 3 > 'raportit/q1 2026.txt'
seq 5 > 'raportit/q2 2026.txt'
seq 2 > raportit/vuosi.txt

# @alku naiivi
find raportit -name '*.txt' | xargs wc -l 2>&1 | sort || true
# @loppu naiivi

# @alku turvallinen
find raportit -name '*.txt' -print0 | sort -z | xargs -0 wc -l
# @loppu turvallinen

# @alku rinnakkain
find raportit -name '*.txt' -print0 \
    | xargs -0 -P 4 -I{} sh -c 'gzip -k "$1" && echo "pakattu: $1"' _ {} \
    | sort
# @loppu rinnakkain
