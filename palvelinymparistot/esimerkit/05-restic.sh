#!/usr/bin/env bash
# Salattu, deduplikoiva varmuuskopio resticillä: kopio, toinen kopio,
# säilytyssääntö, eheystarkistus ja palautustesti. Tulosteesta
# näytetään vain vertailukelpoiset tiedot (tunnisteet ja ajat
# vaihtelevat ajosta toiseen).
set -euo pipefail
export LC_ALL=C
tyo=$(mktemp -d)
trap 'rm -rf "$tyo"' EXIT
cd "$tyo"
mkdir -p data
seq 1 50000 > data/tilaukset.csv
echo "asetukset v1" > data/sovellus.conf

# @alku alustus
export RESTIC_REPOSITORY=$tyo/varasto       # oikeasti esim. s3:... tai
export RESTIC_PASSWORD=opetus-salasana       # sftp:... toiselle koneelle
export RESTIC_CACHE_DIR=$tyo/valimuisti
restic init --quiet
# @loppu alustus

# @alku kopiot
restic backup --quiet --tag paivittainen data
echo "asetukset v2" > data/sovellus.conf
restic backup --quiet --tag paivittainen data
restic snapshots --json | python3 -c '
import json, sys
kopiot = json.load(sys.stdin)
print(f"kopioita {len(kopiot)}")'
# Kopioiden ero: vain muuttunut tiedosto tallentui uudelleen.
mapfile -t tunnisteet < <(restic snapshots --json | python3 -c '
import json, sys
for k in json.load(sys.stdin):
    print(k["short_id"])')
restic diff "${tunnisteet[@]}" | grep -E '^[-+M] '
# @loppu kopiot

# @alku palautus
restic check --quiet && echo "eheystarkistus: ok"
restic restore latest --quiet --target palautus > /dev/null
diff -r data palautus/data && echo "palautustesti: ok"
# @loppu palautus

# @alku sailytys
restic forget --quiet --keep-last 1 --prune > /dev/null
restic snapshots --json | python3 -c '
import json, sys
print(f"säilytyksen jälkeen {len(json.load(sys.stdin))} kopio")'
# @loppu sailytys
