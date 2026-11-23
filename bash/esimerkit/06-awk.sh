#!/usr/bin/env bash
# Suurten tiedostojen laskenta kuuluu awkille: yksi prosessi käsittelee
# kaikki rivit, kun Bash-silmukka kutsuisi ulkoisia komentoja riveittäin.
set -euo pipefail
export LC_ALL=C

# @alku awk
# Kentät: aika polku vasteaika_ms koodi
awk '
    $4 >= 500 { virheet[$2]++ }
    { yht[$2] += $3; n[$2]++ }
    END {
        for (p in yht)
            printf "%-12s %4d ms %d virhettä\n", p, yht[p] / n[p], virheet[p]
    }
' | sort
# @loppu awk
