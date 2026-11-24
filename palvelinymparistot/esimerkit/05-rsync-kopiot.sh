#!/usr/bin/env bash
# Inkrementaaliset kopiot rsyncillä: jokainen kopio näyttää täydeltä,
# mutta muuttumattomat tiedostot ovat kovia linkkejä edelliseen
# kopioon (--link-dest), joten ne eivät vie lisää tilaa.
set -euo pipefail
export LC_ALL=C
tyo=$(mktemp -d)
trap 'rm -rf "$tyo"' EXIT
cd "$tyo"
mkdir -p data/raportit kopiot
head -c 200000 /dev/zero > data/tietokanta.dump
echo "versio 1" > data/raportit/q3.txt
touch -d '2026-11-22 08:00' data/tietokanta.dump data/raportit/q3.txt

# @alku kopio
kopioi() {  # kopioi <nimi>
    local edellinen
    edellinen=$(find kopiot -mindepth 1 -maxdepth 1 -type d \
        | sort | tail -n 1)
    rsync -a --delete ${edellinen:+--link-dest="$PWD/$edellinen"} \
        data/ "kopiot/$1/"
}
# @loppu kopio

kopioi 2026-11-22
echo "versio 2" > data/raportit/q3.txt          # muutos
touch -d '2026-11-23 09:30' data/raportit/q3.txt
kopioi 2026-11-23
rm data/raportit/q3.txt                          # vahingossa poistettu
kopioi 2026-11-24

# @alku tarkastelu
echo "linkkien määrä (tietokanta.dump):"
stat -c '  %h %n' kopiot/*/tietokanta.dump
echo "uutta dataa kopioittain (sama inode lasketaan kerran):"
find kopiot -type f -printf '%P %i %s\n' | sort \
    | awk '{ split($1, p, "/"); if (!($2 in nahty)) uusi[p[1]] += $3
             nahty[$2] = 1 }
           END { for (k in uusi) printf "  %s %d tavua\n", k, uusi[k] }' \
    | sort
# @loppu tarkastelu

# @alku palautus
mkdir palautus
cp -a kopiot/2026-11-23/raportit/q3.txt palautus/
echo "palautettu: $(cat palautus/q3.txt)"
# Palautustesti: koko kopio vastaa lähdettä sen hetkellä.
diff -r data kopiot/2026-11-24 && echo "uusin kopio vastaa lähdettä"
# @loppu palautus
