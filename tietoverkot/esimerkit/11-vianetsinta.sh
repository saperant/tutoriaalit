#!/usr/bin/env bash
# Vianetsintä kerros kerrallaan: kolme tavallista vikaa ja niiden
# tunnistaminen.
#   A 192.0.2.10 ── (192.0.2.1) R (198.51.100.1) ── S 198.51.100.80
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
N=tv-vika$$
A=$N-a R=$N-r S=$N-s
siivoa() {
    for ns in "$A" "$R" "$S"; do ip netns del "$ns" 2>/dev/null; done
}
trap siivoa EXIT

uusi_ns "$A"; uusi_ns "$R"; uusi_ns "$S"
ip -n "$A" link add eth0 type veth peer name lan netns "$R"
ip -n "$R" link add wan type veth peer name eth0 netns "$S"
for pari in "$A eth0" "$R lan" "$R wan" "$S eth0"; do
    read -r ns liitanta <<< "$pari"
    ip -n "$ns" link set "$liitanta" up
done
ip -n "$R" addr add 192.0.2.1/24 dev lan
ip -n "$R" addr add 198.51.100.1/24 dev wan
ip -n "$S" addr add 198.51.100.80/24 dev eth0
ip netns exec "$R" sysctl -qw net.ipv4.ip_forward=1

# a: komento koneessa A, virheilmoitukset mukaan tulosteeseen.
a() { ip netns exec "$A" "$@" 2>&1 || true; }
yhteys() {
    if ip netns exec "$A" ping -c 1 -W 1 198.51.100.80 > /dev/null 2>&1
    then echo "ping S: vastaus"; else echo "ping S: ei vastausta"; fi
}

# @alku vika1
echo "== vika 1: väärä aliverkon maski"
ip -n "$A" addr add 192.0.2.10/32 dev eth0
a ip route get 192.0.2.1
a ip -4 -br addr show dev eth0
ip -n "$A" addr flush dev eth0
ip -n "$A" addr add 192.0.2.10/24 dev eth0
# @loppu vika1

# @alku vika2
echo "== vika 2: oletusyhdyskäytävää ei ole olemassa"
ip -n "$A" route add default via 192.0.2.254
yhteys
a ip route get 198.51.100.80 | head -n 1
a ip -4 neigh show 192.0.2.254
ip -n "$A" route replace default via 192.0.2.1
# @loppu vika2

# @alku vika3
echo "== vika 3: palvelimelta puuttuu paluureitti"
yhteys
ip netns exec "$S" ip route get 192.0.2.10 2>&1 || true
ip -n "$S" route add default via 198.51.100.1
yhteys
# @loppu vika3
