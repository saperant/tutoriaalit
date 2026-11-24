#!/usr/bin/env bash
# Palvelun laatu reunareitittimellä: luottamusraja asettaa DSCP-merkinnän,
# ja HTB-jonotus antaa puheliikenteelle oman, etuoikeutetun luokan
# hitaalla ulospäin menevällä yhteydellä.
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

for s in r isp puhelin tyoasema; do
    solmu "$s"
    # Ilman IPv6:ta linkeillä ei kulje taustaliikennettä, ja laskurit
    # ovat ennustettavia.
    ns "$s" sysctl -qw net.ipv6.conf.default.disable_ipv6=1 \
        2> /dev/null || true
done
linkki r wan isp eth0
linkki puhelin eth0 r puh
linkki tyoasema eth0 r lan
ns r ip addr add 100.64.0.2/30 dev wan
ns isp ip addr add 100.64.0.1/30 dev eth0
ns isp ip route add 10.0.0.0/8 via 100.64.0.2
ns r ip addr add 10.50.0.1/24 dev puh
ns r ip addr add 10.60.0.1/24 dev lan
ns puhelin ip addr add 10.50.0.10/24 dev eth0
ns puhelin ip route add default via 10.50.0.1
ns tyoasema ip addr add 10.60.0.10/24 dev eth0
ns tyoasema ip route add default via 10.60.0.1
ns r sysctl -qw net.ipv4.ip_forward=1
# Kiinteät ARP-merkinnät: wan-linkillä ei kulje ARP-kyselyitä.
ns r ip neigh add 100.64.0.1 lladdr 02:00:00:00:01:02 dev wan nud permanent
ns isp ip neigh add 100.64.0.2 lladdr 02:00:00:00:01:01 dev eth0 \
    nud permanent

# @alku luottamusraja
# Päätelaitteiden omiin merkintöihin ei luoteta: puhelinverkon liikenne
# merkitään EF:ksi ja kaikki muu nollataan.
ns r nft -f - <<'SAANNOT'
table inet qos {
    chain merkinta {
        type filter hook prerouting priority mangle;
        iifname "puh" ip dscp set ef
        iifname != "puh" ip dscp set cs0
    }
}
SAANNOT
# @loppu luottamusraja

# @alku htb
# Ulospäin 10 Mbit/s. Puheelle taattu 2 Mbit/s ja korkein prioriteetti,
# muulle loput. Luokittelu DSCP-kentän (EF = 46 = 0xb8 ToS-tavuna) mukaan.
ns r tc qdisc add dev wan root handle 1: htb default 30
ns r tc class add dev wan parent 1: classid 1:1 htb rate 10mbit
ns r tc class add dev wan parent 1:1 classid 1:10 htb \
    rate 2mbit ceil 10mbit prio 0
ns r tc class add dev wan parent 1:1 classid 1:30 htb \
    rate 8mbit ceil 10mbit prio 1
ns r tc filter add dev wan parent 1: protocol ip u32 \
    match ip dsfield 0xb8 0xfc flowid 1:10
# @loppu htb

ns puhelin ping -q -c 3 -i 0.2 100.64.0.1 > /dev/null
# Työasema yrittää merkitä oman liikenteensä puheeksi (ToS 0xb8).
ns tyoasema ping -q -c 4 -i 0.2 -Q 0xb8 100.64.0.1 > /dev/null

# @alku laskurit
ns r tc -s class show dev wan | awk '
    /^class htb 1:(10|30)/ { luokka = $3 }
    /Sent/ && luokka { print luokka, $4, "pakettia"; luokka = "" }'
# @loppu laskurit
