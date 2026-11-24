#!/usr/bin/env bash
# Nimipalvelu: dnsmasq paikallisen vyöhykkeen palvelimena ja kyselyt
# digillä sekä omalla asiakkaalla.
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
N=tv-dns$$
P=$N-palvelin K=$N-kone
T=$(mktemp -d)
siivoa() {
    if [[ -f $T/pid ]]; then kill "$(cat "$T/pid")" 2>/dev/null || true; fi
    ip netns del "$P" 2>/dev/null || true
    ip netns del "$K" 2>/dev/null || true
    rm -rf "$T"
}
trap siivoa EXIT

uusi_ns "$P"; uusi_ns "$K"
ip -n "$P" link add eth0 type veth peer name eth0 netns "$K"
ip -n "$P" addr add 192.0.2.53/24 dev eth0
ip -n "$K" addr add 192.0.2.10/24 dev eth0
ip -n "$P" link set eth0 up
ip -n "$K" link set eth0 up

# @alku palvelin
# Paikallinen vyöhyke koti.example; muita nimiä ei välitetä eteenpäin.
ip netns exec "$P" dnsmasq \
    --listen-address=192.0.2.53 --bind-interfaces \
    --no-resolv --no-hosts --local=/koti.example/ --local-ttl=300 \
    --host-record=www.koti.example,192.0.2.80 \
    --host-record=nas.koti.example,192.0.2.20 \
    --cname=kuvat.koti.example,nas.koti.example \
    --mx-host=koti.example,posti.koti.example,10 \
    --host-record=posti.koti.example,192.0.2.25 \
    --txt-record=koti.example,"v=spf1 mx -all" \
    --pid-file="$T/pid" --user=root
# @loppu palvelin

# @alku kyselyt
kysy() { ip netns exec "$K" dig +short @192.0.2.53 "$@"; }
kysy www.koti.example A
kysy kuvat.koti.example A
kysy koti.example MX
kysy koti.example TXT
kysy -x 192.0.2.20
ip netns exec "$K" dig @192.0.2.53 puuttuu.koti.example \
    | grep -oE 'status: [A-Z]+'
# @loppu kyselyt

# @alku oma
ip netns exec "$K" python3 "$HAK/09-dns/main.py" \
    kysy 192.0.2.53 kuvat.koti.example A
# @loppu oma
