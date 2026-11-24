#!/usr/bin/env bash
# Kuuntelevat portit ja yhteydet ss-komennolla.
set -euo pipefail
if [[ $EUID -ne 0 ]]; then exec sudo -n -- bash "$0" "$@"; fi
export LC_ALL=C

HAK=$(cd "$(dirname "$0")" && pwd)
NS=tv-portit$$
PALVELIN=""
siivoa() {
    if [[ -n $PALVELIN ]]; then kill "$PALVELIN" 2>/dev/null || true; fi
    ip netns del "$NS" 2>/dev/null || true
}
trap siivoa EXIT
ip netns add "$NS"
ip -n "$NS" link set lo up

# @alku portit
ip netns exec "$NS" python3 "$HAK/07-yhteys.py" palvelin 127.0.0.1 8080 &
PALVELIN=$!
ip netns exec "$NS" python3 -c "import socket, time
u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
u.bind(('0.0.0.0', 5353))
time.sleep(2)" &
sleep 0.5
echo "--- kuuntelevat TCP-portit (-tlnH)"
ip netns exec "$NS" ss -tlnH | awk '{print $1, $4}'
echo "--- UDP-portit"
ip netns exec "$NS" ss -uanH | awk '{print $1, $4}'
ip netns exec "$NS" python3 "$HAK/07-yhteys.py" \
    asiakas 127.0.0.1 8080 portti 45000
# @loppu portit
wait
