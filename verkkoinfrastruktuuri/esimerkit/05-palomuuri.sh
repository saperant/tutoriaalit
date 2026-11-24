#!/usr/bin/env bash
# Palomuuri kolmen vyöhykkeen välissä: lähiverkko (lan), palvelinverkko
# (dmz) ja internet (wan). Oletuksena kaikki estetään; sallitut virrat
# luetellaan. Lähiverkon liikenne naamioidaan (SNAT), ja DMZ:n
# verkkopalvelin julkaistaan porttiohjauksella (DNAT).
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

for s in pm tyoasema palvelin internet; do solmu "$s"; done
linkki tyoasema eth0 pm lan
linkki palvelin eth0 pm dmz
linkki internet eth0 pm wan
ns tyoasema ip addr add 10.0.10.20/24 dev eth0
ns tyoasema ip route add default via 10.0.10.1
ns palvelin ip addr add 10.0.20.80/24 dev eth0
ns palvelin ip route add default via 10.0.20.1
ns internet ip addr add 203.0.113.2/24 dev eth0
# Hyökkääjä yrittää myös suoraan yksityisiin osoitteisiin.
ns internet ip route add 10.0.0.0/16 via 203.0.113.1
ns pm ip addr add 10.0.10.1/24 dev lan
ns pm ip addr add 10.0.20.1/24 dev dmz
ns pm ip addr add 203.0.113.1/24 dev wan
ns pm sysctl -qw net.ipv4.ip_forward=1

# Palvelut: verkkopalvelin DMZ:ssä ja "ulkoinen" palvelin internetissä.
# Molemmat vastaavat yhdellä rivillä, josta näkee asiakkaan osoitteen.
kuuntele() {   # kuuntele SOLMU PORTTI NIMI
    ns "$1" socat "TCP4-LISTEN:$2,fork,reuseaddr" \
        SYSTEM:"echo $3 näkee asiakkaan \$SOCAT_PEERADDR" 2> /dev/null &
}
kuuntele palvelin 80 www
kuuntele palvelin 22 ssh
kuuntele internet 443 ulkoinen
kuuntele tyoasema 22 ssh
odota 10 ns palvelin socat /dev/null TCP:127.0.0.1:80
odota 10 ns internet socat /dev/null TCP:127.0.0.1:443

# @alku saannot
ns pm nft -f - <<'SAANNOT'
table inet palomuuri {
    chain forward {
        type filter hook forward priority filter; policy drop;
        ct state established,related accept
        ct state invalid drop
        iifname "lan" oifname { "wan", "dmz" } accept
        iifname "wan" oifname "dmz" ip daddr 10.0.20.80 tcp dport 80 \
            ct status dnat accept
        counter comment "estetyt"
    }
}
table ip nat {
    chain prerouting {
        type nat hook prerouting priority dstnat;
        iifname "wan" tcp dport 80 dnat to 10.0.20.80
    }
    chain postrouting {
        type nat hook postrouting priority srcnat;
        oifname "wan" masquerade
    }
}
SAANNOT
# @loppu saannot

yhdista() {   # yhdista SOLMU OSOITE PORTTI
    local vastaus
    vastaus=$(ns "$1" socat -T 2 - "TCP:$2:$3,connect-timeout=2" \
        < /dev/null 2> /dev/null) || vastaus="estetty"
    echo "$1 -> $2:$3: $vastaus"
}
# @alku testit
yhdista tyoasema 203.0.113.2 443    # lähiverkosta ulos: sallittu, SNAT
yhdista tyoasema 10.0.20.80 22      # lähiverkosta DMZ:aan: sallittu
yhdista internet 203.0.113.1 80     # julkaistu palvelu: DNAT
yhdista internet 10.0.20.80 22      # suoraan DMZ:aan: estetty
yhdista palvelin 10.0.10.20 22      # DMZ:sta lähiverkkoon: estetty
# @loppu testit
