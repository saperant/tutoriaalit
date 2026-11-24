#!/usr/bin/env bash
# Kaappaus tiedostoon ja sen tulkinta omalla pcap-lukijalla.
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
N=tv-kaap$$
A=$N-a B=$N-b
T=$(mktemp -d)
siivoa() {
    ip netns del "$A" 2>/dev/null || true
    ip netns del "$B" 2>/dev/null || true
    rm -rf "$T"
}
trap siivoa EXIT
uusi_ns "$A"; uusi_ns "$B"
ip -n "$A" link add eth0 type veth peer name eth0 netns "$B"
ip -n "$A" addr add 192.0.2.10/24 dev eth0
ip -n "$B" addr add 192.0.2.20/24 dev eth0
ip -n "$A" link set eth0 up
ip -n "$B" link set eth0 up

# @alku kaappaus
# Suodatin (BPF) rajaa jo kaapattaessa: vain kone B, ei SSH:ta.
ip netns exec "$A" tcpdump --immediate-mode -Z root -i eth0 -n \
    -w "$T/liikenne.pcap" 'host 192.0.2.20 and not port 22' \
    2> "$T/loki" &
TCPDUMP=$!
until grep -q listening "$T/loki" 2>/dev/null; do sleep 0.1; done
ip netns exec "$A" ping -c 3 -i 0.2 192.0.2.20 > /dev/null
for portti in 53 123 514; do
    ip netns exec "$A" python3 -c "import socket as s
u = s.socket(s.AF_INET, s.SOCK_DGRAM)
u.bind(('', 40000 + $portti))
u.sendto(b'x', ('192.0.2.20', $portti))"
done
sleep 0.3
kill -INT "$TCPDUMP"; wait "$TCPDUMP" || true
python3 "$HAK/11-pcap.py" "$T/liikenne.pcap"
# @loppu kaappaus
