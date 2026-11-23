#!/usr/bin/env bash
# Vasteajat päätepisteittäin: määrä, keskiarvo ja maksimi.
set -euo pipefail
export LC_ALL=C

# @alku aineisto
cat > vasteajat.log <<'LOKI'
GET /tuotteet 200 42
GET /tuotteet 200 38
POST /tilaukset 201 310
GET /tilaukset 500 1250
GET /tuotteet 200 51
POST /tilaukset 201 280
GET /tilaukset 200 95
LOKI
# @loppu aineisto

# @alku awk
awk '{
    avain = $1 " " $2
    n[avain]++; summa[avain] += $4
    if ($4 > maks[avain]) maks[avain] = $4
}
END {
    for (a in n)
        printf "%-16s %3d %8.1f %6d\n", a, n[a], summa[a] / n[a], maks[a]
}' vasteajat.log | sort
# @loppu awk

# @alku ehto
awk '$3 >= 500 { print NR ": " $0 }' vasteajat.log
awk -v raja=300 '$4 > raja { hitaat++ } END { print hitaat + 0 }' \
    vasteajat.log
# @loppu ehto
