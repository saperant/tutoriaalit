#!/usr/bin/env bash
# Pikaoppaan putkireseptit testattuina.
set -euo pipefail
export LC_ALL=C

printf '%s\n' b a c a b a > nimet.txt
mkdir -p src
printf 'vanha_nimi()\n' > src/a.c
printf 'x = vanha_nimi\n' > src/b.py
printf 'muu\n' > src/c.c
printf 'id,arvo\n1,5\n2,7\n3,1\n' > data.csv

# @alku reseptit
sort nimet.txt | uniq -c | sort -k1,1nr | head -n 2   # yleisimmät
awk '!nahty[$0]++' nimet.txt | paste -sd' '   # duplikaatit pois
grep -rlZ 'vanha_nimi' src | sort -z \
    | xargs -0 sed -i 's/vanha_nimi/uusi_nimi/g'     # korvaus puussa
grep -rc 'uusi_nimi' src | sort
awk -F, 'NR > 1 { s += $2 } END { print s }' data.csv     # summa
# @loppu reseptit

# @alku awk
awk -F, -v raja=4 'NR > 1 && $2 > raja { s[$1] += $2 }
    END { for (k in s) printf "%-4s %5.1f\n", k, s[k] }' data.csv | sort
# @loppu awk
