#!/usr/bin/env bash
# CSV-raportti: myynti tuoteryhmittäin ja osuus kokonaismyynnistä.
set -euo pipefail
export LC_ALL=C

# @alku aineisto
cat > myynti.csv <<'CSV'
pvm,tuoteryhma,tuote,kpl,hinta
2026-11-02,kirjat,Algoritmit,2,49.90
2026-11-02,elektroniikka,USB-kaapeli,5,7.50
2026-11-03,kirjat,Linux-opas,1,39.00
2026-11-03,ruoka,Kahvi,10,8.95
2026-11-04,elektroniikka,Kuulokkeet,1,89.00
CSV
# @loppu aineisto

# @alku raportti
awk -F, 'NR > 1 {
    myynti[$2] += $4 * $5; yhteensa += $4 * $5
}
END {
    for (r in myynti)
        printf "%-14s %8.2f %5.1f %%\n", r, myynti[r],
               100 * myynti[r] / yhteensa
    printf "%-14s %8.2f\n", "kaikki", yhteensa
}' myynti.csv | sort -k2,2nr
# @loppu raportti
