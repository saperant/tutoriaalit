#!/usr/bin/env bash
# OSPF kolmen reitittimen renkaassa. Kun yksi yhteys katkeaa, reitit
# lasketaan uudelleen toista kautta.
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

for r in r1 r2 r3; do solmu "$r"; done
# Siirtoyhteydet: r1–r2 172.16.12.0/30, r2–r3 .23.0/30, r3–r1 .13.0/30
siirto() {   # siirto A B VERKKO
    linkki "$1" "$2" "$2" "$1"
    ns "$1" ip addr add "172.16.$3.1/30" dev "$2"
    ns "$2" ip addr add "172.16.$3.2/30" dev "$1"
}
siirto r1 r2 12
siirto r2 r3 23
siirto r1 r3 13

# @alku bird
# Kunkin reitittimen lähiverkko on silta lan (10.0.N.0/24). BIRD vie
# opitut reitit ytimen reititystauluun.
for n in 1 2 3; do
    r="r$n"
    ns "$r" ip link add lan type bridge
    ns "$r" ip link set dev lan up
    ns "$r" ip addr add "10.0.$n.1/24" dev lan
    ns "$r" sysctl -qw net.ipv4.ip_forward=1
    cat > "$LABRA_HAK/$r.conf" <<KONF
router id 10.0.$n.1;
protocol device {}
protocol kernel { ipv4 { export all; }; }
protocol ospf v2 {
    ipv4 { import all; };
    area 0 {
        interface "r*" { type ptp; hello 1; dead 3; };
        interface "lan" { stub yes; };
    };
}
KONF
    ns "$r" bird -c "$LABRA_HAK/$r.conf" -s "$LABRA_HAK/$r.ctl" \
        -P "$LABRA_HAK/$r.pid"
done
# @loppu bird

reitti() {   # reitti SOLMU KOHDE: mitä kautta kohde saavutetaan
    ns "$1" ip route show "$2" | awk '{print $1, "via", $3, "dev", $5}'
}
opittu() { [[ -n $(ns "$1" ip route show "$2" proto bird) ]]; }

odota 30 opittu r1 10.0.2.0/24
odota 30 opittu r1 10.0.3.0/24
echo "Alussa:"
reitti r1 10.0.2.0/24
reitti r1 10.0.3.0/24

# @alku katko
# Yhteys r1–r2 katkeaa. Naapuruus raukeaa dead-ajan jälkeen, ja r1
# laskee lyhimmät polut uudelleen.
ns r1 ip link set dev r2 down
kautta_r3() { ns r1 ip route show 10.0.2.0/24 | grep -q 172.16.13.2; }
odota 30 kautta_r3
# @loppu katko
echo "Katkon jälkeen:"
reitti r1 10.0.2.0/24
reitti r1 10.0.3.0/24
