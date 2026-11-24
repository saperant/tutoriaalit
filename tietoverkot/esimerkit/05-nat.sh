#!/usr/bin/env bash
# Osoitteenmuunnos (NAT): kotiverkon koneet näkyvät ulos reitittimen
# osoitteella.
#   A 192.168.1.10 ── (192.168.1.1) R (203.0.113.5) ── P 203.0.113.80
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
N=tv-nat$$
A=$N-a R=$N-r P=$N-p
T=$(mktemp -d)
siivoa() {
    for ns in "$A" "$R" "$P"; do ip netns del "$ns" 2>/dev/null; done
    rm -rf "$T"
}
trap siivoa EXIT

uusi_ns "$A"; uusi_ns "$R"; uusi_ns "$P"
ip -n "$A" link add eth0 type veth peer name lan netns "$R"
ip -n "$R" link add wan type veth peer name eth0 netns "$P"
for pari in "$A eth0" "$R lan" "$R wan" "$P eth0"; do
    read -r ns liitanta <<< "$pari"
    ip -n "$ns" link set "$liitanta" up
done
ip -n "$A" addr add 192.168.1.10/24 dev eth0
ip -n "$A" route add default via 192.168.1.1
ip -n "$R" addr add 192.168.1.1/24 dev lan
ip -n "$R" addr add 203.0.113.5/24 dev wan
ip -n "$P" addr add 203.0.113.80/24 dev eth0
ip netns exec "$R" sysctl -qw net.ipv4.ip_forward=1
# Palvelin P ei tiedä mitään yksityisestä verkosta 192.168.1.0/24.

# kaappaa: näyttää ensimmäisen palvelimelle saapuvan pingin.
kaappaa() {
    ip netns exec "$P" tcpdump --immediate-mode -Z root -i eth0 -n -t \
        -c 1 icmp 2> "$T/virhe" > "$T/kaappaus" &
    local pid=$!
    for _ in $(seq 50); do
        grep -q listening "$T/virhe" 2>/dev/null && break
        sleep 0.1
    done
    ip netns exec "$A" ping -c 1 -W 1 203.0.113.80 > /dev/null 2>&1 \
        && echo "vastaus" || echo "ei vastausta"
    # Jos mitään ei saapunut, tcpdump lopetetaan.
    sleep 0.3; kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
    sed -E 's/, id [0-9]+, seq [0-9]+, length [0-9]+//' "$T/kaappaus"
}

echo "--- ilman NAT:ia"
kaappaa
# @alku nat
ip netns exec "$R" nft -f - <<'NFT'
table ip nat {
    chain postrouting {
        type nat hook postrouting priority srcnat;
        oifname "wan" masquerade
    }
}
NFT
# @loppu nat
echo "--- NAT päällä"
kaappaa
