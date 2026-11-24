#!/usr/bin/env bash
# MTU, polun MTU:n selvitys ja IPv4-pakettien pilkkominen.
#   A ── R ── B, jossa R–B-linkin MTU on 1400 tavua.
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
N=tv-mtu$$
A=$N-a R=$N-r B=$N-b
T=$(mktemp -d)
siivoa() {
    for ns in "$A" "$R" "$B"; do ip netns del "$ns" 2>/dev/null; done
    rm -rf "$T"
}
trap siivoa EXIT

uusi_ns "$A"; uusi_ns "$R"; uusi_ns "$B"
ip -n "$A" link add eth0 type veth peer name lan netns "$R"
ip -n "$R" link add wan type veth peer name eth0 netns "$B"
ip -n "$A" addr add 192.0.2.10/24 dev eth0
ip -n "$R" addr add 192.0.2.1/24 dev lan
ip -n "$R" addr add 198.51.100.1/24 dev wan
ip -n "$B" addr add 198.51.100.20/24 dev eth0
for pari in "$A eth0" "$R lan" "$R wan" "$B eth0"; do
    read -r ns liitanta <<< "$pari"
    ip -n "$ns" link set "$liitanta" up
done
ip -n "$A" route add default via 192.0.2.1
ip -n "$B" route add default via 198.51.100.1
ip netns exec "$R" sysctl -qw net.ipv4.ip_forward=1
# @alku mtu
ip -n "$R" link set wan mtu 1400
ip -n "$B" link set eth0 mtu 1400
# @loppu mtu

# @alku df
# 1472 tavua dataa + 8 ICMP + 20 IP = 1500 tavua, "älä pilko" (DF).
ip netns exec "$A" ping -c 1 -W 1 -M "do" -s 1472 198.51.100.20 \
    | grep -oE 'Frag needed.*' || true
ip netns exec "$A" ip route get 198.51.100.20 | grep -oE 'mtu [0-9]+'
# 1372 + 8 + 20 = 1400 mahtuu.
ip netns exec "$A" ping -c 1 -W 1 -M "do" -s 1372 198.51.100.20 \
    | grep -oE '[0-9]+ received'
# @loppu df

# @alku pilkonta
ip netns exec "$B" tcpdump --immediate-mode -Z root -i eth0 -n -t -v \
    -c 2 icmp 2> "$T/loki" > "$T/kaappaus" &
TCPDUMP=$!
until grep -q listening "$T/loki" 2>/dev/null; do sleep 0.1; done
ip netns exec "$A" ping -c 1 -W 1 -M dont -s 1472 198.51.100.20 \
    | grep -oE '[0-9]+ received'
wait "$TCPDUMP"
# Kaksi palaa: kumpikin on oma IP-pakettinsa, ja vain ensimmäisessä
# on ICMP-otsake. Lippu [+] = lisää paloja tulossa (MF).
LAUSEKE='offset [0-9]+, flags \[[^]]*\], proto [A-Z]+ \([0-9]+\)'
grep -oE "$LAUSEKE, length [0-9]+" "$T/kaappaus"
# @loppu pilkonta
