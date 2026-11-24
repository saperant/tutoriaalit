#!/usr/bin/env bash
# Kytkin oppii MAC-osoitteet ja välittää kehykset vain oikeaan porttiin.
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

solmu kytkin
for h in h1 h2 h3; do
    solmu "$h"
done
# @alku silta
ns kytkin ip link add br0 type bridge
ns kytkin ip link set br0 up
i=1
for h in h1 h2 h3; do
    linkki "$h" eth0 kytkin "p$i"
    ns kytkin ip link set "p$i" master br0
    ns "$h" ip addr add "10.0.0.$i/24" dev eth0
    i=$((i + 1))
done
# @loppu silta

tavoittaa h1 10.0.0.2
tavoittaa h1 10.0.0.3
# @alku fdb
# Opitut osoitteet: kytkimen välitystaulu (forwarding database).
ns kytkin bridge fdb show br br0 dynamic | awk '{print $1, $3}' | sort
# @loppu fdb
