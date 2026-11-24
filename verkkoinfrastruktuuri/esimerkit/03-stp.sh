#!/usr/bin/env bash
# Kolme kytkintä renkaassa: STP katkaisee silmukan estämällä yhden portin.
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

# @alku stp
# Pienin prioriteetti voittaa: k1 on juurisilta. Ajastimet ovat
# senttisekunteja; lyhyet arvot nopeuttavat laboratoriota.
prio=(4096 8192 12288)
for i in 0 1 2; do
    k="k$((i + 1))"
    solmu "$k"
    ns "$k" ip link add br0 type bridge stp_state 1 \
        priority "${prio[$i]}" forward_delay 200 hello_time 100
    ns "$k" ip link set br0 up
done
# Rengas k1–k2–k3–k1. Portti on nimetty naapurin mukaan.
for pari in "k1 k2" "k2 k3" "k3 k1"; do
    read -r x y <<< "$pari"
    linkki "$x" "$y" "$y" "$x"
    ns "$x" ip link set dev "$y" master br0
    ns "$y" ip link set dev "$x" master br0
done
# @loppu stp

# Odotetaan, että kaikki portit ovat lopullisessa tilassa.
valmis() {
    local k
    for k in k1 k2 k3; do
        if ns "$k" bridge link show | grep -qE 'state (listening|learning)'
        then return 1; fi
    done
}
odota 30 valmis
# @alku tilat
for k in k1 k2 k3; do
    ns "$k" bridge link show | awk -v k="$k" '{
        portti = $2; sub(/[@:].*/, "", portti)
        for (i = 1; i < NF; i++) if ($i == "state") tila = $(i + 1)
        print k, "->", portti ": " tila }'
done
# @loppu tilat
