#!/usr/bin/env bash
# Kaksi aliverkkoa ja niiden välinen reititin.
#   A 192.0.2.10 ── (192.0.2.1) R (198.51.100.1) ── B 198.51.100.20
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
N=tv-reit$$
A=$N-a R=$N-r B=$N-b
siivoa() {
    for ns in "$A" "$R" "$B"; do ip netns del "$ns" 2>/dev/null; done
}
trap siivoa EXIT

# kaapeli NS1 LIITÄNTÄ1 NS2 LIITÄNTÄ2
kaapeli() {
    ip -n "$1" link add "$2" type veth peer name "$4" netns "$3"
    ip -n "$1" link set "$2" up
    ip -n "$3" link set "$4" up
}

# @alku verkko
uusi_ns "$A"; uusi_ns "$R"; uusi_ns "$B"
kaapeli "$A" eth0 "$R" lan
kaapeli "$R" wan "$B" eth0
ip -n "$A" addr add 192.0.2.10/24 dev eth0
ip -n "$R" addr add 192.0.2.1/24 dev lan
ip -n "$R" addr add 198.51.100.1/24 dev wan
ip -n "$B" addr add 198.51.100.20/24 dev eth0
# Uusi nimiavaruus voi periä asetuksen isäntäkoneelta: aloitetaan
# varmasti tilasta, jossa reititin ei välitä paketteja.
ip netns exec "$R" sysctl -qw net.ipv4.ip_forward=0
# @loppu verkko

kokeile() {
    if ip netns exec "$A" ping -c 1 -W 1 198.51.100.20 > /dev/null 2>&1
    then echo "A -> B: vastaus"; else echo "A -> B: ei yhteyttä"; fi
}

# @alku vaiheet
echo "1. ei reittiä"
kokeile
ip -n "$A" route add default via 192.0.2.1
ip -n "$B" route add default via 198.51.100.1
echo "2. reitit, mutta R ei välitä paketteja"
kokeile
ip netns exec "$R" sysctl -qw net.ipv4.ip_forward=1
echo "3. välitys päällä"
kokeile
ip netns exec "$A" ping -c 1 198.51.100.20 | grep -oE 'ttl=[0-9]+'
ip -n "$A" route
ip -n "$A" route get 198.51.100.20 | head -n 1
ip -n "$R" route
# @loppu vaiheet
