#!/usr/bin/env bash
# Käynnistää palvelimen ja kaksi asiakasta paikallisesti ja tulostaa
# niiden raportit aina samassa järjestyksessä.
set -euo pipefail
bin=${1:?käyttö: aja.sh BIN-HAKEMISTO}
hak=$(mktemp -d)
trap 'kill $(jobs -p) 2> /dev/null || true; rm -rf "$hak"' EXIT

timeout 30 "$bin/palvelin" "$hak/portti" > "$hak/palvelin.txt" &
palvelin=$!
for _ in $(seq 100); do
    [[ -s $hak/portti ]] && break
    sleep 0.05
done
portti=$(cat "$hak/portti")
timeout 30 "$bin/asiakas" 1 "$portti" > "$hak/asiakas1.txt" &
a1=$!
timeout 30 "$bin/asiakas" 2 "$portti" > "$hak/asiakas2.txt" &
a2=$!
wait "$palvelin" "$a1" "$a2"
cat "$hak/palvelin.txt" "$hak/asiakas1.txt" "$hak/asiakas2.txt"
