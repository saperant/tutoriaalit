#!/usr/bin/env bash
# Liikennevirtojen seuranta NetFlow v9:llä: reitittimen softflowd koostaa
# paketit virroiksi ja lähettää ne keräimelle (nfcapd). Raportti kertoo,
# kuka puhui kenelle ja mihin palveluun, ilman pakettien sisältöä.
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

for s in asiakas reititin palvelin keruu; do solmu "$s"; done
linkki asiakas eth0 reititin lan
linkki reititin dmz palvelin eth0
linkki reititin hallinta keruu eth0
ns asiakas ip addr add 10.10.0.10/24 dev eth0
ns asiakas ip route add default via 10.10.0.1
ns palvelin ip addr add 10.20.0.80/24 dev eth0
ns palvelin ip route add default via 10.20.0.1
ns keruu ip addr add 10.99.0.9/24 dev eth0
ns reititin ip addr add 10.10.0.1/24 dev lan
ns reititin ip addr add 10.20.0.1/24 dev dmz
ns reititin ip addr add 10.99.0.1/24 dev hallinta
ns reititin sysctl -qw net.ipv4.ip_forward=1

# @alku keruu
# Keräin ja reitittimen kaappaus. Laboratoriossa kaapattu liikenne
# muunnetaan virroiksi jälkikäteen (softflowd -r); tuotannossa softflowd
# kuuntelee liitäntää jatkuvasti (-i lan) tai virrat tuottaa reititin itse.
mkdir -p "$LABRA_HAK/virrat"
ns keruu nfcapd -w "$LABRA_HAK/virrat" -p 2055 > /dev/null 2>&1 &
PCAP=$LABRA_HAK/lan.pcap
ns reititin tcpdump -i lan --immediate-mode -U -Z root -w "$PCAP" \
    > /dev/null 2>&1 &
# @loppu keruu
kuuntelee() { ns keruu ss -lun | grep -q ':2055 '; }
odota 10 kuuntelee
kaappaa() { test -s "$PCAP"; }
odota 10 kaappaa

# Liikennettä: kaksi verkkosivupyyntöä ja yksi nimikysely.
ns palvelin socat TCP-LISTEN:80,fork,reuseaddr SYSTEM:"echo ok" \
    2> /dev/null &
odota 10 ns palvelin socat /dev/null TCP:127.0.0.1:80
for _ in 1 2; do
    ns asiakas socat -T 2 - TCP:10.20.0.80:80 < /dev/null > /dev/null
done
ns asiakas socat -T 1 - UDP:10.20.0.80:53 <<< "kysely" \
    > /dev/null 2>&1 || true

# @alku raportti
juuri pkill -INT -f "tcpdump .* -w $PCAP"
sleep 0.5
ns reititin softflowd -r "$PCAP" -n 10.99.0.9:2055 -v 9 \
    > /dev/null 2>&1
sleep 0.5
# Keräin kirjoittaa tiedostonsa loppuun, kun se pysäytetään.
juuri pkill -TERM -f "nfcapd -w $LABRA_HAK/virrat"
sleep 0.5
# Koosteena virrat palveluihin (kohdeportti < 1024) ja niiden määrä.
nfdump -q -R "$LABRA_HAK/virrat" -A proto,srcip,dstip,dstport \
    -o 'fmt:%pr %sa -> %da:%dp %fl' 'dst port < 1024' |
    sort | awk '{$1 = $1; print $0 " virtaa"}'
# @loppu raportti
