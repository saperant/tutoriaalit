#!/usr/bin/env bash
# Kolme konetta Linux-sillalla (ohjelmistokytkin) ja kytkimen oppimat
# MAC-osoitteet.
set -euo pipefail
if [[ $EUID -ne 0 ]]; then exec sudo -n -- bash "$0" "$@"; fi
export LC_ALL=C
# Konteissa /proc/sys on usein vain luettavissa, mutta nimiavaruuksien
# asetukset (sysctl) on voitava kirjoittaa.
if [[ ! -w /proc/sys/net/ipv4/ip_forward ]]; then
    mount -o remount,rw /proc/sys
fi

# @alku uusi-ns
# Luo verkkonimiavaruuden. Esimerkit käyttävät IPv4:ää, joten IPv6
# kytketään pois, jotta tulosteet ovat samat kaikilla koneilla.
uusi_ns() {
    ip netns add "$1"
    if [[ -d /proc/sys/net/ipv6 ]]; then
        ip netns exec "$1" sysctl -qw net.ipv6.conf.all.disable_ipv6=1 \
            net.ipv6.conf.default.disable_ipv6=1
    fi
}
# @loppu uusi-ns

N=tv-silta$$
KYTKIN=$N-kytkin
siivoa() {
    for ns in "$KYTKIN" "$N-a" "$N-b" "$N-c"; do
        ip netns del "$ns" 2>/dev/null || true
    done
}
trap siivoa EXIT

# @alku kytkin
uusi_ns "$KYTKIN"
ip -n "$KYTKIN" link add br0 type bridge
ip -n "$KYTKIN" link set br0 up

# kone NIMI NUMERO: luo koneen ja kytkee sen kytkimen porttiin.
kone() {
    local ns=$N-$1 nro=$2
    uusi_ns "$ns"
    ip -n "$ns" link add eth0 address "02:00:00:00:00:0$nro" type veth \
        peer name "portti$nro" netns "$KYTKIN"
    ip -n "$ns" addr add "192.0.2.$nro/24" dev eth0
    ip -n "$ns" link set eth0 up
    ip -n "$KYTKIN" link set "portti$nro" master br0 up
}
kone a 1
kone b 2
kone c 3
# @loppu kytkin

# @alku liikenne
ping_yhteenveto() {
    ip netns exec "$N-$1" ping -c 1 -W 1 "$2" \
        | grep -oE '[0-9]+ received'
}
ping_yhteenveto a 192.0.2.2
ping_yhteenveto a 192.0.2.3

echo "--- A:n ARP-taulu"
ip -n "$N-a" -4 neigh show dev eth0 | awk '{print $1, $3}' | sort
echo "--- kytkimen oppimat osoitteet"
bridge -n "$KYTKIN" fdb show br br0 \
    | grep -v permanent | awk '{print $1, $3}' | sort
# @loppu liikenne
