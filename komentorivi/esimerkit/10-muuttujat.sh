#!/usr/bin/env bash
# shellcheck disable=SC2016  # lapsikuori laajentaa muuttujat
# Kuoren muuttuja, ympäristömuuttuja ja kertaluonteinen asetus.
set -euo pipefail
export LC_ALL=C
unset TILA PALVELU_PORTTI

# @alku muuttujat
nayta='echo "lapsi näkee: TILA=${TILA:-<ei>} PORTTI=${PALVELU_PORTTI:-<ei>}"'
TILA=kehitys
bash -c "$nayta"
export TILA
bash -c "$nayta"
PALVELU_PORTTI=9090 bash -c "$nayta"
echo "kuoressa: PORTTI=${PALVELU_PORTTI:-<ei>}"
env -i bash -c "$nayta"
# @loppu muuttujat
