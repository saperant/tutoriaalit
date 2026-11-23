#!/usr/bin/env bash
# CSV-tiedostot cutilla, sortilla ja joinilla. Kentissä ei saa olla
# lainattuja pilkkuja; muuten tarvitaan oikea CSV-jäsennin.
set -euo pipefail
export LC_ALL=C

# @alku aineisto
cat > asiakkaat.csv <<'CSV'
id,nimi,kaupunki
3,Laura,Tampere
1,Kaisa,Oulu
2,Matti,Helsinki
CSV
cat > tilaukset.csv <<'CSV'
tilaus,asiakas,summa
T-7,2,129.90
T-8,1,15.00
T-9,2,49.50
T-10,3,310.00
CSV
# @loppu aineisto

# @alku lajittelu
tail -n +2 tilaukset.csv | sort -t, -k3,3nr | head -n 2
# @loppu lajittelu

# @alku join
join -t, -1 1 -2 2 -o 1.2,2.1,2.3 \
    <(tail -n +2 asiakkaat.csv | sort -t, -k1,1) \
    <(tail -n +2 tilaukset.csv | sort -t, -k2,2) \
    | sort
# @loppu join

# @alku cut
cut -d, -f2,3 --output-delimiter=': ' asiakkaat.csv | tail -n +2
# @loppu cut
# @loppu cut
