#!/usr/bin/env bash
# Kaksi L2-segmenttiä reititetyn runkoverkon yli VXLANilla. h1 ja h2 ovat
# segmentissä 100, h3 segmentissä 200. Kaikilla on sama aliverkko, mutta
# eri segmentit eivät näe toisiaan.
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

for s in l1 l2 h1 h2 h3; do solmu "$s"; done
# Runkoverkko: lehtikytkimet l1 ja l2 (VTEP) suoraan yhteydessä.
linkki l1 runko l2 runko
ns l1 ip addr add 172.16.0.1/30 dev runko
ns l2 ip addr add 172.16.0.2/30 dev runko

# @alku vtep
# segmentti KYTKIN VNI PAIKALLINEN ETÄ: silta ja VXLAN-tunneli
segmentti() {
    ns "$1" ip link add "br$2" type bridge
    ns "$1" ip link add "vx$2" type vxlan id "$2" dstport 4789 \
        local "$3" remote "$4" dev runko
    ns "$1" ip link set dev "vx$2" master "br$2"
    ns "$1" ip link set dev "vx$2" up
    ns "$1" ip link set dev "br$2" up
}
segmentti l1 100 172.16.0.1 172.16.0.2
segmentti l2 100 172.16.0.2 172.16.0.1
segmentti l2 200 172.16.0.2 172.16.0.1
# @loppu vtep

liita() {   # liita ISÄNTÄ KYTKIN VNI OSOITE
    linkki "$1" eth0 "$2" "$1"
    ns "$2" ip link set dev "$1" master "br$3"
    ns "$1" ip addr add "$4/24" dev eth0
}
liita h1 l1 100 10.10.0.1
liita h2 l2 100 10.10.0.2
liita h3 l2 200 10.10.0.3

tavoittaa h1 10.10.0.2
tavoittaa h1 10.10.0.3
