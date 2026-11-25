#!/usr/bin/env bash
# Piirtää Makefilen riippuvuusverkon Graphvizin DOT-muodossa.
#
#   make -pn [KOHDE] | ./verkko.sh > verkko.dot
#
# make -p tulostaa Maken tietokannan: jokaisen kohteen ja sen
# riippuvuudet sellaisina kuin Make ne Makefilen ja mukaan luettujen
# tiedostojen jälkeen näkee. -n estää komentojen ajamisen. Verkkoon
# otetaan tiedostojen väliset riippuvuudet; valekohteet (.PHONY),
# Maken erikoiskohteet ja hakemistot jätetään pois.
set -euo pipefail

awk '
    /^# Files/               { tiedostot = 1; next }
    /^# files hash-table/    { tiedostot = 0 }
    !tiedostot               { next }
    /^# Not a target:/       { ohita = 1; next }
    /^[^#\t][^=]*:/ {
        if (ohita) { ohita = 0; next }
        kohde = $0; sub(/:.*/, "", kohde)
        riippuvuudet = $0; sub(/^[^:]*:+ */, "", riippuvuudet)
        sub(/ *\|.*/, "", riippuvuudet)   # järjestysriippuvuudet pois
        if (kohde == ".PHONY") {
            n = split(riippuvuudet, osat, " ")
            for (i = 1; i <= n; i++) vale[osat[i]] = 1
        }
        if (kohde ~ /^\./ || kohde == "Makefile") next
        n = split(riippuvuudet, osat, " ")
        for (i = 1; i <= n; i++) kaari[osat[i] " " kohde] = 1
    }
    END {
        for (k in kaari) {
            split(k, p, " ")
            if (p[1] in vale || p[2] in vale) continue
            if (p[1] ~ /\.d$/ || p[2] ~ /\.d$/) continue
            printf "  \"%s\" -> \"%s\";\n", p[1], p[2]
        }
    }
' | LC_ALL=C sort | {
    echo "digraph {"
    echo "  rankdir=LR; nodesep=0.25; ranksep=0.6;"
    cat
    echo "}"
}
