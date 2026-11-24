#!/usr/bin/env bash
# Multicast DNS: nimi .local-verkossa ilman nimipalvelinta.
set -euo pipefail
if [[ $EUID -ne 0 ]]; then exec sudo -n -- bash "$0" "$@"; fi
export LC_ALL=C
# Konteissa /proc/sys on usein vain luettavissa, mutta nimiavaruuksien
# asetukset (sysctl) on voitava kirjoittaa.
if [[ ! -w /proc/sys/net/ipv4/ip_forward ]]; then
    mount -o remount,rw /proc/sys
fi

uusi_ns() {
    ip netns add "$1"
    if [[ -d /proc/sys/net/ipv6 ]]; then
        ip netns exec "$1" sysctl -qw net.ipv6.conf.all.disable_ipv6=1 \
            net.ipv6.conf.default.disable_ipv6=1
    fi
}
HAK=$(cd "$(dirname "$0")" && pwd)
N=tv-mdns$$
A=$N-a B=$N-b
VASTAAJA=""
siivoa() {
    if [[ -n $VASTAAJA ]]; then kill "$VASTAAJA" 2>/dev/null || true; fi
    ip netns del "$A" 2>/dev/null || true
    ip netns del "$B" 2>/dev/null || true
}
trap siivoa EXIT

uusi_ns "$A"; uusi_ns "$B"
ip -n "$A" link add eth0 type veth peer name eth0 netns "$B"
ip -n "$A" addr add 192.0.2.10/24 dev eth0
ip -n "$B" addr add 192.0.2.30/24 dev eth0
for ns in "$A" "$B"; do
    ip -n "$ns" link set eth0 up
    # @alku reitti
    # Ryhmälähetysosoitteille reitti liitäntään.
    ip -n "$ns" route add 224.0.0.0/4 dev eth0
    # @loppu reitti
done

# @alku kysely
ip netns exec "$B" python3 "$HAK/09-dns/main.py" \
    mdns-vastaa tulostin.local 192.0.2.30 &
VASTAAJA=$!
sleep 0.5
echo "B:n ryhmäjäsenyydet:"
ip -n "$B" maddr show dev eth0 | awk '$1 == "inet" {print "  " $2}' | sort
ip netns exec "$A" python3 "$HAK/09-dns/main.py" mdns-kysy tulostin.local
wait "$VASTAAJA"
# @loppu kysely
