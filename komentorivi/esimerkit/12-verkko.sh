#!/usr/bin/env bash
# Verkon perustyökalut: HTTP-pyyntöjä omalla koneella ajettavaan
# palvelimeen.
set -euo pipefail
export LC_ALL=C
export no_proxy=127.0.0.1 NO_PROXY=127.0.0.1

# Paikallinen web-palvelin, jota vasten komentoja kokeillaan.
mkdir sivusto
echo "Tervehdys palvelimelta" > sivusto/tervehdys.txt
python3 -m http.server 18412 --bind 127.0.0.1 --directory sivusto \
    > /dev/null 2>&1 &
palvelin=$!
sammuta() {
    kill "$palvelin" 2> /dev/null || true
    wait "$palvelin" 2> /dev/null || true
}
trap sammuta EXIT
for _ in $(seq 50); do
    curl -fsS -o /dev/null http://127.0.0.1:18412/ 2> /dev/null && break
    sleep 0.1
done

# @alku verkko
osoite=http://127.0.0.1:18412

curl -fsS "$osoite/tervehdys.txt"
curl -sS -o /dev/null -w 'tilakoodi %{http_code}\n' "$osoite/puuttuu.txt"
curl -fsS "$osoite/puuttuu.txt" 2> /dev/null || echo "curl: paluuarvo $?"
curl -sI "$osoite/tervehdys.txt" | tr -d '\r' | grep -i '^content-'
curl -fsS -o kopio.txt "$osoite/tervehdys.txt" && wc -c kopio.txt
# @loppu verkko
