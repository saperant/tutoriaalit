#!/usr/bin/env bash
# Palvelimen oma palomuuri (input-ketju): SSH vain hallintaverkosta,
# uusien yhteyksien määrä rajoitetaan lähdeosoitteittain, ja sallitut
# ylläpitokoneet ovat nimetyssä joukossa, jota voi muuttaa sääntöihin
# koskematta.
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

for s in palvelin kytkin yllapito hyokkaaja; do solmu "$s"; done
ns kytkin ip link add br0 type bridge
ns kytkin ip link set dev br0 up
for s in palvelin yllapito hyokkaaja; do
    linkki "$s" eth0 kytkin "$s"
    ns kytkin ip link set dev "$s" master br0
done
ns palvelin ip addr add 10.99.0.10/24 dev eth0
ns yllapito ip addr add 10.99.0.5/24 dev eth0
ns hyokkaaja ip addr add 10.99.0.66/24 dev eth0
ns palvelin socat TCP-LISTEN:22,fork,reuseaddr SYSTEM:"echo ssh" \
    2> /dev/null &
odota 10 ns palvelin socat /dev/null TCP:127.0.0.1:22

# @alku saannot
ns palvelin nft -f - <<'SAANNOT'
table inet suojaus {
    set yllapitokoneet {
        type ipv4_addr
        elements = { 10.99.0.5 }
    }
    chain input {
        type filter hook input priority filter; policy drop;
        iif "lo" accept
        ct state established,related accept
        ct state invalid drop
        icmp type echo-request limit rate 10/second accept
        # Ylläpitokoneet: aina sallittu.
        ip saddr @yllapitokoneet tcp dport 22 accept
        # Muut: korkeintaan kolme uutta yhteyttä minuutissa osoitetta
        # kohden (dynaaminen joukko eli mittari).
        tcp dport 22 ct state new add @ssh_yritykset \
            { ip saddr limit rate 3/minute burst 3 packets } accept
        counter comment "pudotetut"
    }
    set ssh_yritykset {
        type ipv4_addr
        flags dynamic
        timeout 5m
    }
}
SAANNOT
# @loppu saannot

yrita() {   # yrita SOLMU KERTOJA
    local i tulos=""
    for ((i = 1; i <= $2; i++)); do
        if ns "$1" socat -T 1 - TCP:10.99.0.10:22,connect-timeout=1 \
            < /dev/null > /dev/null 2>&1; then tulos+="+"; else tulos+="-"
        fi
    done
    echo "$1: $tulos"
}
# @alku kokeilu
yrita hyokkaaja 5
yrita yllapito 5
# Uusi ylläpitokone lisätään joukkoon; säännöt pysyvät ennallaan.
ns palvelin nft add element inet suojaus yllapitokoneet '{ 10.99.0.66 }'
yrita hyokkaaja 2
# @loppu kokeilu
