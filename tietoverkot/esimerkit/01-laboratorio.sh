#!/usr/bin/env bash
# Kaksi konetta yhdellä kaapelilla: verkkonimiavaruudet laboratoriona.
set -euo pipefail
# Verkkonimiavaruudet vaativat pääkäyttäjän oikeudet.
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

# @alku luonti
A=tv-lab$$-a
B=tv-lab$$-b
trap 'ip netns del "$A" 2>/dev/null; ip netns del "$B" 2>/dev/null' EXIT

uusi_ns "$A"
uusi_ns "$B"
# Virtuaalinen kaapeli (veth-pari): pää eth0 kummassakin koneessa.
ip -n "$A" link add eth0 address 02:00:00:00:00:0a type veth \
    peer name eth0 netns "$B" address 02:00:00:00:00:0b
ip -n "$A" addr add 192.0.2.1/24 dev eth0
ip -n "$B" addr add 192.0.2.2/24 dev eth0
ip -n "$A" link set eth0 up
ip -n "$B" link set eth0 up
# @loppu luonti

# @alku tarkastelu
ip -n "$A" -br link
ip -n "$A" -4 -br addr
ip netns exec "$A" ping -c 3 -i 0.2 192.0.2.2 \
    | grep -oE '[0-9]+ packets transmitted, [0-9]+ received'
ip -n "$A" -4 neigh show dev eth0
# @loppu tarkastelu
