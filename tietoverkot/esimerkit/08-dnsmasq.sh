#!/usr/bin/env bash
# DHCP: dnsmasq jakaa osoitteet, asiakas hakee osoitteen (DORA).
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
N=tv-dhcp$$
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
ip -n "$P" link add eth0 type veth peer name eth0 netns "$K" \
    address 02:00:00:00:00:0b
ip -n "$P" addr add 192.0.2.1/24 dev eth0
ip -n "$P" link set eth0 up
ip -n "$K" link set eth0 up
# Osoitteeton liitäntä: paluureitin tarkistus (rp_filter) hylkäisi
# palvelimen vastauksen. Oikeat asiakkaat käyttävät raakasokeetteja.
ip netns exec "$K" sysctl -qw net.ipv4.conf.all.rp_filter=0 \
    net.ipv4.conf.eth0.rp_filter=0

# @alku palvelin
ip netns exec "$P" dnsmasq \
    --port=0 --no-ping \
    --interface=eth0 --bind-interfaces \
    --dhcp-range=192.0.2.100,192.0.2.150,255.255.255.0,1h \
    --dhcp-sequential-ip \
    --dhcp-option=option:router,192.0.2.1 \
    --dhcp-option=option:dns-server,192.0.2.53 \
    --dhcp-host=02:00:00:00:00:0c,192.0.2.42,tulostin \
    --dhcp-leasefile="$T/vuokrat" --pid-file="$T/pid" --user=root
# @loppu palvelin

# @alku asiakas
# Liitännällä ei ole vielä osoitetta; asiakas lähettää yleislähetyksiä.
ip netns exec "$K" python3 "$HAK/08-dhcp.py" \
    asiakas eth0 02:00:00:00:00:0b > "$T/asiakas"
cat "$T/asiakas"
read -r OSOITE REITITIN < <(tail -n 1 "$T/asiakas")
ip -n "$K" addr add "$OSOITE" dev eth0
ip -n "$K" route add default via "$REITITIN"
ip -n "$K" -4 -br addr show dev eth0
ip -n "$K" route show default
# @loppu asiakas

# @alku vuokrat
# Vuokratiedosto: päättymisaika, MAC, osoite, nimi, asiakastunniste.
awk '{print "vuokra:", $2, $3}' "$T/vuokrat"
# @loppu vuokrat
